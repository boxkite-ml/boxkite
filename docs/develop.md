# Developing boxkite

## Releasing

Update `setup.py` with your new version.

Set up your env with your PyPI token.

```
cp .env.template .env
<edit .env>
```

```
./build.sh
./publish.sh
```
