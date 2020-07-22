# Neuron

## SETUP
1. Make sure you have `virtualenv` installed
2. Run the env creation script `./create_env.sh`. If you get a permission denied error run `chmod +x ./create_env.sh`
3. To activate your environment in the future you can run `source venv/bin/activate` from the root directory. To see what virtual env you are in run `echo $VIRTUAL_ENV`
4. If you ever make a dependency change or install something, make sure the tests pass and then run `pip freeze > requirements.txt` to push the updates

## Starting the Service
`flask run` from the root directory
Make sure to `export FLASK_APP=run.py`

## AWS
To connect to AWS it is requied that the auth id and token are stored in ~/.aws/credentials``

