# Changelog

<!--next-version-placeholder-->

## v1.18.12 (2023-07-27)
### Fix
* Don't overwrite base logging Handler class lock var ([#108](https://github.com/logdna/python/issues/108)) ([`5b04d72`](https://github.com/logdna/python/commit/5b04d72b42686d926fb5e73dadb2d7a1ba16d9c3))

## v1.18.11 (2023-07-26)
### Fix
* Remove Thread/event to fix Django regression ([#107](https://github.com/logdna/python/issues/107)) ([`0337a09`](https://github.com/logdna/python/commit/0337a09433953227dabb0b65da8583e8f9273986))

## v1.18.10 (2023-07-26)
### Fix
* Utilize apikey header for auth to make compatible with pipelines ([#104](https://github.com/logdna/python/issues/104)) ([`5394e97`](https://github.com/logdna/python/commit/5394e9714779878cd415a4566cd44d9183e150b9))

## v1.18.9 (2023-07-21)
### Fix
* Make flush thread a daemon thread to prevent shutdown hang ([#102](https://github.com/logdna/python/issues/102)) ([`17a69b0`](https://github.com/logdna/python/commit/17a69b044de43a7a9d7d3e6eb65a0c60f1fa23f0))

## v1.18.8 (2023-07-18)
### Fix
* Bump semver ([#101](https://github.com/logdna/python/issues/101)) ([`913e5f4`](https://github.com/logdna/python/commit/913e5f4f35f2920a6b2162022b93495b4774654c))

## v1.18.7 (2023-05-05)
### Fix
* Gate buils from non maintainers ([`97803b5`](https://github.com/logdna/python/commit/97803b55a102539a75b0763891c1d27757460067))

## v1.18.6 (2023-01-27)
### Fix
* Added retries for http 429 504 ([#93](https://github.com/logdna/python/issues/93)) ([`712d81d`](https://github.com/logdna/python/commit/712d81d4ab2bfbf95d65898fb365a5bcb1396199))

## v1.18.5 (2023-01-27)
### Fix
* **chore:** Upgraded pytest to resolve security vulnerability in py <= 1.11.0 ([#92](https://github.com/logdna/python/issues/92)) ([`905b06a`](https://github.com/logdna/python/commit/905b06a648e19896087b0c51ba1e055212727560))

## v1.18.4 (2023-01-06)
### Fix
* Dependabot -> Vulnerabilities -> cryptography >= 37.0.0 < 38.0.3 ([#91](https://github.com/logdna/python/issues/91)) ([`7ccde50`](https://github.com/logdna/python/commit/7ccde50ba50c0abbec1a7efe4dd665e8b35511c0))

## v1.18.3 (2022-12-07)
### Fix
* Add documentation for log_error_response option ([#88](https://github.com/logdna/python/issues/88)) ([`d5bf85c`](https://github.com/logdna/python/commit/d5bf85ca26579e0186e1abdbcd1b6c44c60c9eca))

## v1.18.2 (2022-05-10)
### Fix
* Requests error handling ([#82](https://github.com/logdna/python/issues/82)) ([`e412859`](https://github.com/logdna/python/commit/e4128592aa9c2301c6467115148f2f23f88da9d3))

## v1.18.1 (2021-11-18)
### Fix
* **threading:** Account for secondary buffer flush and deadlock ([`d00b952`](https://github.com/logdna/python/commit/d00b9529d116ddf9ba454462d4d804dc54423c83))

## v1.18.0 (2021-07-26)
### Fix
* **opts:** Repair logging options for each call ([`e326e4c`](https://github.com/logdna/python/commit/e326e4c2461b808b5d3a885b37555f8e610615e4))

## v1.17.0 (2021-07-15)
### Feature
* **meta:** Enable adding custom meta fields ([`f250237`](https://github.com/logdna/python/commit/f250237dbde932e99ab199023516f66a248c5e80))
* **threadWorkerPools:** Introduce extra threads ([`9bfe479`](https://github.com/logdna/python/commit/9bfe479132acb0aa8e5784f2aa31298606e49789))

### Documentation
* Update the README as requested ([`5dd754f`](https://github.com/logdna/python/commit/5dd754f177675eb25cd5d5449bd3bcc8286f8739))

## v1.16.0 (2021-04-15)


## v1.15.0 (2021-04-15)


## v1.14.0 (2021-04-15)


## v1.13.0 (2021-04-15)


## v1.12.0 (2021-04-15)


## v1.11.0 (2021-04-15)


## v1.10.0 (2021-04-15)


## v1.9.0 (2021-04-15)


## v1.8.0 (2021-04-15)


## v1.7.0 (2021-04-07)


## v1.6.0 (2021-04-07)
### Feature
* **ci:** Enable releases through semantic release ([`9e4b1c0`](https://github.com/logdna/python/commit/9e4b1c0a43bc0941ba4fb336ea12a3f497622ee6))
* **ci:** Include jenkins setup ([`1c5be37`](https://github.com/logdna/python/commit/1c5be37ef32776f2d0ba2b68b67cebb58b1f0177))
* **tasks:** Convert run scripts to tasks ([`f5a8b18`](https://github.com/logdna/python/commit/f5a8b182941a0c514594cbaa7a3ac5952173d5a8))
* **lint:** Setup linting + test harness ([`0a7763a`](https://github.com/logdna/python/commit/0a7763a2befbf598b59d7ab595b19e22b173fda5))
* **tags:** Allow tags to be configured ([`6adc21e`](https://github.com/logdna/python/commit/6adc21e872fa521be1aaf08309f7f3d0ba3dc5c5))
* **meta:** Python log info in meta object ([`cf9b505`](https://github.com/logdna/python/commit/cf9b505734df12918a665a8a8c74d4fd74e5bc47))
* **handlers:** Make available via config file ([`39c5dec`](https://github.com/logdna/python/commit/39c5decd98e8d4feb6c1bbfa487faf35396c8b12))

### Fix
* **ci:** Correct invalid environment variable ([`fce4d59`](https://github.com/logdna/python/commit/fce4d5995b31c426f2b66992b57f129f22f9f18f))

### Documentation
* Add @matthiasfru as a contributor ([`3727bc3`](https://github.com/logdna/python/commit/3727bc3386d3dd6465e0b0d15675a091a3743c24))
* Add @rudyryk as a contributor ([`9ab0e39`](https://github.com/logdna/python/commit/9ab0e3932180c41bff1cd0944c24fb8e208f4391))
* Add @kurtiss as a contributor ([`1476085`](https://github.com/logdna/python/commit/14760857649b56207240bae907386a33f7f1666b))
* Update @inkrement as a contributor ([`6a2cede`](https://github.com/logdna/python/commit/6a2cedef6695e18a981a3605176c9cffdd159827))
* Add @inkrement as a contributor ([`7ba6992`](https://github.com/logdna/python/commit/7ba6992287f98c478da72f5982a0869b5d835df7))
* Add @btashton as a contributor ([`c1e69bf`](https://github.com/logdna/python/commit/c1e69bfc965e1e1e5717ec7af3271dc0bf6b502d))
* Add @SpainTrain as a contributor ([`7b9f04b`](https://github.com/logdna/python/commit/7b9f04b86a1e813bccea29ea8db1554808ea48b6))
* Add @sataloger as a contributor ([`04081f0`](https://github.com/logdna/python/commit/04081f039d6136a66b259f7245ad7845ef1c080a))
* Add @jdemaeyer as a contributor ([`69e8f7c`](https://github.com/logdna/python/commit/69e8f7cc0782a778d0da230ff1a8feb5f8cee352))
* Add @dchai76 as a contributor ([`42e9c6b`](https://github.com/logdna/python/commit/42e9c6bddc2bce29714072bba37d85d9a734eac2))
* Add @danmaas as a contributor ([`23bbab4`](https://github.com/logdna/python/commit/23bbab48cdef4aaef6813459dbdb23dbd9c60374))
* Add @LYHuang as a contributor ([`3cc9e23`](https://github.com/logdna/python/commit/3cc9e232d0b12b9f0315efb1d618426b486a2604))
* Add @baronomasia as a contributor ([`8971bd7`](https://github.com/logdna/python/commit/8971bd713d74cd9386c60a50cc75a7fc3591f544))
* Add @utek as a contributor ([`ea495b4`](https://github.com/logdna/python/commit/ea495b479cc0549ff68a1e816c3f7a174c1c138c))
* Add @esatterwhite as a contributor ([`0a334bd`](https://github.com/logdna/python/commit/0a334bdb5690049634c64eb0f9c6c1026b9ab001))
* Add @mikehu as a contributor ([`e7aa7cb`](https://github.com/logdna/python/commit/e7aa7cb2624313c065f7bbc8a129c1a4841f9ec2))
* Add @vilyapilya as a contributor ([`e3191f5`](https://github.com/logdna/python/commit/e3191f577fb7ddf7590ca1e1bf239f66d2f30fd0))
* Add @smusali as a contributor ([`4d5022f`](https://github.com/logdna/python/commit/4d5022f93948cca239ebc104e34034c350956f65))
* Add @respectus as a contributor ([`85a543c`](https://github.com/logdna/python/commit/85a543c9dc27a3c6064e790be0ba1c475187c38d))
