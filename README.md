# mint
Beta version of the mint

Currently this service can:
- Sign data.
- Verify signed data
- Sign and post data to the System of Record service.

NB: currently it is doing this with test public and private keys held within the test_keys folder.

##dependencies:
- python 2 (needed for the encryption modules)
- contents of the requirements.txt

The run.sh script will use VirtualEnv and VirtualEnvWrapper if it finds it.

##how to run in development

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
source ~/venvs/system-of-record/bin/activate
```

```
./run.sh -d
```

To the run this in production use the following command

```
./run.sh
```

##how to run tests

In virtual machine

```
./test.sh
```
The tests output a results.xml which is in junit format.

##Example curls

Note:  Use 0.0.0.0 when running from host.  Use 10.0.2.2 when calling from another VM.

To get signed data post something like this:

```
curl -X POST -d '{"titleno" : "DN1"}' -H "Content-Type: application/json" http://10.0.2.2:5000/sign
```

To verify signed data post something like this:

```
curl -X POST -d '{"sig" : "b6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ", "data":{"titleno" : "DN1"}}' -H "Content-Type: application/json" http://10.0.2.2:5000/verify
```

To sign and store something on system of record:

```
curl -X POST -d '{"titleno" : "DN1"}' -H "Content-Type: application/json" http://10.0.2.2:5000/insert
```
