Telegram bot for aviline tech support.

Implemented:
- bot start / bot end
- (router) start -> buy -> select_product -> product_description
- (router) start -> support -> select_product -> product_problems
- (router) start -> buy / support -> contact_us

Todo:
- Codestyle
  - Clean code, you lazy pal!
  - add flake8 (black) linter to project
- Admin:
  - connect django_admin, to manage the products from web ✅ (models created through django, then replicated with pydantic :/)
  - connect database instead of pyfile ✅ (database scheme must be added below)
- Configs:
  - implement through pydantic (Do I really need this?)
  - add python_loadenv ✅ (env file path is config/.env, can be adjusted or system env can be used)
- Constants:
  - Add email verification regexp (Must write tests)
  - revise constants file ✅ (all moved to env + config/settings)
- Templates:
  - Develop the templates visual design ✅ (implemented as jinja engine tgbot.utils.template_engine)
  - Implement templates through Jinja2 ✅ (templates are html files with jinja variables)
- Navigation:
  - monkey test bot operation from scratch
  - implement reversing (<< back) logics ✅ (going dfs until see node with required state)
- Readme.md
  - add pictures to describe bot operation logic
  - add pictures to describe bot architecture
- Database (check corner cases)
  - Products and problems should have boolean field that shows if they are active or not 
  - Connection object from factory ✅ (tgbot.database.connection.get_connection_pool)
  - Implement async-postgres / aiosqlite database options ✅ (currently async sqlite MUST USE above 3.35? or 3.25?)
  - case #1. Product was deleted when client used bot (Must I check for consistency in every route???)
  - case #2. ProductProblem can have multiple reasons and solutions
- Celery/mediaStorage
  - Clear media storage in case of idle time (moving this to redis, TTL will limit the file lifetime)
- Errors
  - Where and how to handle occurring exceptions
  - 