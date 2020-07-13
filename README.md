# Neuron

## SETUP
1. Create a virtual env and activate it with python 3.6
2. `pip install -r requirements.txt` to install dependencies and the entire package locally
3. run `pip install -e .` to install neuron as a package
3. If you ever make a dependency change or install something, make sure the tests pass and then run `pip freeze > requirements.txt` to push the updates

## Starting the Service
`python3 main.py` will run the service (it will start reading from SQS)
To connect to AWS it is requied that the auth id and token are stored in ~/.aws/credentials``

