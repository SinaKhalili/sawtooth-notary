# Hyperledger Sawtooth Notary
Application for distrbuted systems class to create a simple notary to record house sales on the blockchain with hyperledger sawtooth.


Run with `docker-compose up --build` in root directory. It should start the validator.

Attach to the client with  `docker exec -it notary-client bash` in a separate terminal.  


There is only a single command to add a sale to the blockchain.

`./notary-client`

And you will prompted to enter the name of the buyer, seller, and house information. 

If you want to use the event viewer, run `docker exec -it notary-client bash` in a another terminal again
and begin the events listener with `python3 events-client.py`. 
To see an event, enter a new sale with `./notary-client` in a separate terminal.

Useful docs reference [here](https://sawtooth.hyperledger.org/docs/core/releases/1.0.1/introduction.html)

And useful example ref by a sawtooth dev [here](github.com/inteldan/sawtooth-cookiejar)
