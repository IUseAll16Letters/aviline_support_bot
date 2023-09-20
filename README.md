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
  - connect django_admin, to manage the products from web ✅
  - connect database instead of pyfile ✅
- Configs:
  - implement through pydantic 
  - add python_loadenv ✅
- Constants:
  - Add email verification regexp ✅
  - revise constants file 
- Templates:
  - Develop the templates visual design ✅
  - Implement templates through Jinja2 ✅
- Navigation:
  - monkey test bot operation from scratch
  - implement reversing (<< back) logics ✅
- Readme.md
  - add pictures to describe bot operation logic
  - add pictures to describe bot architecture
- Database (check corner cases)
  - Products and problems should have boolean field that shows if they are active or not
  - Connection object from factory ✅
  - Implement async-postgres / aiosqlite database options
  - case #1. Product was deleted when client used bot
  - case #2. ProductProblem can have multiple reasons and solutions
- Celery/mediaStorage
  - Clear media storage in case of idle time
- Errors
  - Where and how to handle occurring exceptions
  - 