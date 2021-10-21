# Shoppingify API

Shoppingify is a coding challenge by [devchallenges](http://devchallenges.io/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the necessary packages.

```bash
pip install -r requirements.txt
```

## Usage

Create a .env file in the "api" directory, with the following variables:

| DB_CONNECTION="sqlite:///./database/data.db" |
| -------------------------------------------- |
| APP_NAME="Shoppingify"                       |
| DEBUG_MODE=True                              |
| HOST='0.0.0.0'                               |
| PORT=8000                                    |
| secret='your_secret_key'                     |
| algorithm=HS256                              |
| DOMAIN='http://0.0.0.0:8000/'                |

```python
python run.py
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
