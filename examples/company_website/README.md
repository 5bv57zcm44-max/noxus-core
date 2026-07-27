# Company website example

Generate this reproducibly with:

```bash
noxusai new website --name company-website --database postgres --auth both \
  --modules company,website,navigation,hero,about,services,portfolio,team,testimonials,faqs,blog,contact,media,seo,social,legal --docker --yes
```

The generator test suite builds the equivalent full application, migrates it, runs Django checks,
and executes its emitted tests on SQLite. PostgreSQL is selected for Docker and production.
