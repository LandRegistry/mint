# Mint
Beta version of the mint.

Currently this service can:
- Sign data
- Verify signed data
- Sign and post data to the System of Record service

NB: Currently it is doing this with test public and private keys held within the test_keys folder.

##Dependencies:
- Python 2 (needed for the encryption modules)
- Contents of the requirements.txt

The run.sh script will use VirtualEnv and VirtualEnvWrapper if it finds it.

##How to run in development

```
vagrant up
```

```
vagrant ssh
```

```
cd /vagrant
```

```
./run.sh -d
```

To the run this in production use the following command

```
./run.sh
```

##How to run tests

In virtual machine

```
./test.sh
```
The tests output a results.xml which is in junit format.

##Example curls

Note:  Use 127.0.0.1 when running from host.  Use 10.0.2.2 when calling from another VM.

To get signed data post something like this:

```
curl -X POST -d '{"title_number" : "DN1"}' -H "Content-Type: application/json" http://10.0.2.2:5000/sign
```

To verify signed data post something like this:

```
curl -X POST -d '{"sig" : "xGM837iKCZDNUX2031XlPDKLsQ8y6uFs2_1DXqjATUjkAbWS5WFq2hR6MnWDgXC95rjg8h5lmKSUV-8c0W8WSaVaRfjEBz5vFOY3HtU0gXggXSYfLlKoEYT-c4BfySVwxWk1wSuE1F3tHJshJ4Dzx85brJJ6UePE2ZG8oczbBEQxhh09MDtaskNbtmpN8Pd43Ct7SJhHJqHbNT812mZjmoMqp9WJln0N0MDSh0_2Oc-cttJkIToW2AvniiTeK9TMEXo7xRPdkObYuG8gYEWlyKT981gnFz3TgKJJyMjQZTmrUCzcEEb4pMzKoc9jqiivJLD900KgoiC8MtcgNX7Kmw", "data":{"title_number" : "DN1"}}' -H "Content-Type: application/json" http://10.0.2.2:5000/verify
```

To sign and store something on system of record:

```
curl -X POST -d '{"title_number" : "DN1"}' -H "Content-Type: application/json" http://10.0.2.2:5000/insert
```
