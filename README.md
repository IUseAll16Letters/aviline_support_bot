Telegram bot for aviline tech support.

Implemented:
- bot start / bot end
- (router) start -> buy -> select_product -> product_description
- (router) start -> support -> select_product -> product_problems
- (router) start -> buy / support -> contact_us

Todo:
- Overall
  - Clean code, you lazy pal!
- Admin:
  - connect django_admin, to manage the products from web
  - connect database instead of pyfile
- Configs:
  - implement through pydantic
  - add python_loadenv
- Constants:
  - Add email verification regexp ✅
  - revise constants file
- Templates:
  - Develop the templates visual design ✅
  - Implement templates through Jinja2 ✅
- Navigation:
  - monkey test bot operation from scratch
  - implement reversing (<< back) logics
- Readme.md
  - add pictures to describe bot operation logic
  - add pictures to describe bot architecture
