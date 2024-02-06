# LawTech checker streamlit app

By default, we use the OpenAI LLM (though you can customize, see `src/utils.py`). As a result you need to specify an `OPENAI_API_KEY` in an secrets.toml file in `.streamlit` folder.

Create a `.streamlit` folder in the root of the project and create a `secrets.toml` file in it.

Example `secrets.toml` file:

```
OPENAI_API_KEY = "<openai_api_key>"
```
