# mint
Beta version of the mint

Currently this service can:
- Sign data.
- Verify signed data
- Sign and post data to the System of Record service.

##dependencies:
- python 2 (needed for the encryption modules)
- contents of the requirements.txt

##how to run

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
./run.sh
```

##how to run tests
In virtual machine

```
./test.sh
```

##Example curls

To get signed data post something like this:

```
curl -X POST -d '{"titleno" : "DN1"}' -H "Content-Type: application/json" http://192.168.50.4:5010/sign
```

To verify signed data post something like this:

```
curl -X POST -d '{"sig" : "b6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ", "data":{"titleno" : "DN1"}}' -H "Content-Type: application/json" http://192.168.50.4:5010/verify
```

To sign and store something on system of record:

```
curl -X POST -d '{"titleno" : "DN1"}' -H "Content-Type: application/json" http://192.168.50.4:5010/insert
```
