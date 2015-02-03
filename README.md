# mint
Beta version of the mint

Under construction.

##dependencies:
- python 2 (needed for the encryption modules)
- contents of the requirements.txt

##how to run

```
python run.py
```

##Example curls

To get signed data post something like this:

```
curl -X POST -d '{"titleno" : "DN1"}' -H "Content-Type: application/json" http://0.0.0.0:5010/sign
```

To verify signed data post something like this:

```
curl -X POST -d '{"signature" : "b6vjrGcLzq97_2D5h286TkRu_Kf0GonPDsndkGjhtrTBlHKIcF5H18hu635VEork_kr811ZS7B-4FuaCQFk6CvIQpNhxaMxI7m56HRQnj8ZsRSkX74xEKQUqf3k26ZdkODWJVsKyd_grJ39tfwMvJJb9V5REpRa8qXGr1eXgK4gEqwmo2fkow_W8q_yqMTTm9jOuVeFaqCQzAJBFUEWgkuTLRd91Wm8MlF4RhG_w1YktGzVath3tvaiTXNfiyfZbzPu9viotpP81gsFpWw6xocrUDbKhhXw2rm0BU2NvqSMXJ3X1qZs-VZibnWRJNNyt3sFapDojlDs99cL_uQ2aBQ", "data":{"titleno" : "DN1"}}' -H "Content-Type: application/json" http://0.0.0.0:5010/verify
```
