#!/bin/bash

[ -f ./test_chain.pid ] && kill `cat ./test_chain.pid`
truffle develop --log &
echo $! > ./test_chain.pid
