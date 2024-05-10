auto_sqlamin 基于sqladmin，通过动态配置类，无需写ORM代码，快速搭建一个简单的admin 
# 1. 安装依赖包：
    pip install fastapi 
    pip install sqlalchemy 
    pip install sqladmin 
    pip install alembic 
    pip install pytz 
    pip install aiosqlite 
    pip install itsdangerous 
    pip install python-jose 
# 2. 启动服务：
    python main.py

# 3. 访问测试：
    http://127.0.0.1:8000/admin
    用户：admin
    密码：admin

# 4. 使用教程
    1. 新建表
    2. 新建类
    3. 新建属性：（默认创建类时会自动创建id、name、create_date、update_date四个属性）
    4. 新建（约束、索引、外键、关系）根据需要：
    5. 执行编译
    6. 执行迁移
    7. 新建视图：完善参数设置
    8. 权限控制：
        1. 默认管理员可以看到所有内容
        2. 普通用户可以通过绑定角色，并在视图设置中关联角色控制菜单权限
        ![D071021C-0238-44d6-94BC-22EA29DF1510](https://github.com/maxiaojunwolf/auto_sqladmin/assets/34365493/cf2b1fea-a84a-44e6-a3f6-4ca00244e192)

# 5. 说明：
    1. 如何修改默认ORM，执行迁移: 通过设置alembic.env.dynamic_only属性控制迁移固定类还是动态类
    2. 如何扩展动态类的视图设置：
    
        from sqladmin import action
        from starlette.responses import RedirectResponse
        from apps.core.admin.base import CoreModelView
   
        @DynamicModelView.extend_view
        class DemoEntity:
            """扩展动态View"""
    
            # 对应entity.name
            __maps_to__ = "demo_entity"
    
            @action(
                name="demo_action",
                label="示例Action",
                confirmation_message="确认执行示例Action?",
                add_in_detail=False,
                add_in_list=True,
            )
            async def my_action(self, request):
    
                return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    3. 对于已经删除的表，系统不会删除物理表，需要手动删除
# 6 存在问题：
    1. 属性为bool类型的,默认值为True，新建时checked未生效
    2. readonly对于关系和枚举类型不生效
