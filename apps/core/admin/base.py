# -*- coding: utf-8 -*-
from functools import wraps
from typing import Any, Type, no_type_check

from sqladmin import ModelView, Admin
from sqladmin.authentication import login_required
from sqladmin.forms import get_model_form
from sqladmin.helpers import secure_filename, stream_to_csv
from sqladmin.models import ModelViewMeta
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, StreamingResponse
from wtforms import Form

from apps.core.enums import Action
from apps.core.tools import format_datetime


class MyAdmin(Admin):
    """自定义Admin,获取form时传入当前操作类型"""

    @login_required
    async def create(self, request: Request) -> Response:
        """扩展父类方法，model_view.scaffold_form方法中增加action参数"""

        await self._create(request)

        identity = request.path_params["identity"]
        model_view = self._find_model_view(identity)

        Form = await model_view.scaffold_form(action=Action.Create)
        form_data = await self._handle_form_data(request)
        form = Form(form_data)

        context = {
            "model_view": model_view,
            "form": form,
        }

        if request.method == "GET":
            return await self.templates.TemplateResponse(
                request, model_view.create_template, context
            )

        if not form.validate():
            return await self.templates.TemplateResponse(
                request, model_view.create_template, context, status_code=400
            )

        form_data_dict = self._denormalize_wtform_data(form.data, model_view.model)
        try:
            obj = await model_view.insert_model(request, form_data_dict)
        except Exception as e:
            context["error"] = str(e)
            return await self.templates.TemplateResponse(
                request, model_view.create_template, context, status_code=400
            )

        url = self.get_save_redirect_url(
            request=request,
            form=form_data,
            obj=obj,
            model_view=model_view,
        )
        return RedirectResponse(url=url, status_code=302)

    @login_required
    async def edit(self, request: Request) -> Response:
        """扩展父类方法，model_view.scaffold_form方法中增加action参数"""

        await self._edit(request)

        identity = request.path_params["identity"]
        model_view = self._find_model_view(identity)

        model = await model_view.get_object_for_edit(request.path_params["pk"])
        if not model:
            raise HTTPException(status_code=404)

        Form = await model_view.scaffold_form(action=Action.Edit)
        context = {
            "obj": model,
            "model_view": model_view,
            "form": Form(obj=model, data=self._normalize_wtform_data(model)),
        }

        if request.method == "GET":
            return await self.templates.TemplateResponse(
                request, model_view.edit_template, context
            )

        form_data = await self._handle_form_data(request, model)
        form = Form(form_data)
        if not form.validate():
            context["form"] = form
            return await self.templates.TemplateResponse(
                request, model_view.edit_template, context, status_code=400
            )

        form_data_dict = self._denormalize_wtform_data(form.data, model)
        try:
            if model_view.save_as and form_data.get("save") == "Save as new":
                obj = await model_view.insert_model(request, form_data_dict)
            else:
                obj = await model_view.update_model(
                    request, pk=request.path_params["pk"], data=form_data_dict
                )
        except Exception as e:
            context["error"] = str(e)
            return await self.templates.TemplateResponse(
                request, model_view.edit_template, context, status_code=400
            )

        url = self.get_save_redirect_url(
            request=request,
            form=form_data,
            obj=obj,
            model_view=model_view,
        )
        return RedirectResponse(url=url, status_code=302)


class MyModelViewMeta(ModelViewMeta):
    """自定义元类"""

    @no_type_check
    def __new__(mcls, name, bases, attrs: dict, **kwargs: Any):
        """允许使用attrs中的model，方便使用type创建动态view"""
        if not kwargs.get("model"):
            kwargs["model"] = attrs.get("model")
        return super().__new__(mcls, name, bases, attrs, **kwargs)


class CoreModelView(ModelView, metaclass=MyModelViewMeta):
    """自定义基础View，区分新建和编辑的form_widget_args参数"""
    # 列格式化
    column_type_formatters = dict(ModelView.column_type_formatters,
                                  create_date=format_datetime,
                                  update_date=format_datetime
                                  )
    # 表单默认隐藏列
    form_excluded_columns = ["id", "create_date", "update_date", "creator", "updater"]
    # 新建时表单属性配置
    form_widget_args_create = {}
    # 编辑时表单属性配置
    form_widget_args_edit = {}


    def is_visible(self, request: Request) -> bool:
        """权限控制"""
        return request._current_user.is_superuser

    def is_accessible(self, request: Request) -> bool:
        """权限控制"""
        return request._current_user.is_superuser

    async def scaffold_form(self, action: Action = None) -> Type[Form]:
        """扩展原有方法，根据操作类型选择form_widget_args"""
        if self.form is not None:
            return self.form
        if action == Action.Create:
            form_widget_args = self.form_widget_args_create
        elif action == Action.Edit:
            form_widget_args = self.form_widget_args_edit
        else:
            form_widget_args = self.form_widget_args
        return await get_model_form(
            model=self.model,
            session_maker=self.session_maker,
            only=self._form_prop_names,
            column_labels=self._column_labels,
            form_args=self.form_args,
            form_widget_args=form_widget_args,
            form_class=self.form_base_class,
            form_overrides=self.form_overrides,
            form_ajax_refs=self._form_ajax_refs,
            form_include_pk=self.form_include_pk,
            form_converter=self.form_converter,
        )

    async def _export_csv(self, data):
        """覆盖默认方法，解决导出时中文乱码问题"""

        async def generate(writer):
            # Append the column titles at the beginning
            yield writer.writerow(self._export_prop_names)

            for row in data:
                vals = [
                    str(await self.get_prop_value(row, name))
                    for name in self._export_prop_names
                ]
                yield writer.writerow(vals)

        # `get_export_name` can be subclassed.
        # So we want to keep the filename secure outside that method.
        filename = secure_filename(self.get_export_name(export_type="csv"))

        res = StreamingResponse(
            content=stream_to_csv(generate),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
        # 设置编码
        res.charset = "utf-8-sig"
        return res

    async def insert_model(self, request: Request, data: dict) -> Any:
        """新建时自动添加创建人"""
        if hasattr(self.model, "creator_id"):
            data["creator_id"] = request._current_user.id
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> Any:
        """更新时自动添加更新人"""
        if hasattr(self.model, "updater_id"):
            data["updater_id"] = request._current_user.id
        return await super().update_model(request, pk, data)




class DynamicModelView(CoreModelView):
    """动态View基类"""
    # 保存动态view的扩展类
    _extend_dynamic_views = {}

    @classmethod
    def extend_view(cls, extend_class):
        """扩展动态view功能"""
        if not getattr(extend_class, "__maps_to__", None):
            raise Exception("{}类__maps_to__参数缺失".format(str(extend_class)))
        cls._extend_dynamic_views[extend_class.__maps_to__] = extend_class

        @wraps(extend_class)
        def wrapper(*args, **kwargs):
            """保存映射"""
            return extend_class(*args, **kwargs)

        return wrapper

    def is_visible(self, request: Request) -> bool:
        """权限控制"""
        if request._current_user.is_superuser:
            return True
        return self.model.__entity__["name"] in request._current_user.visible_menus

    def is_accessible(self, request: Request) -> bool:
        """权限控制"""
        if request._current_user.is_superuser:
            return True
        return self.model.__entity__["name"] in request._current_user.visible_menus
