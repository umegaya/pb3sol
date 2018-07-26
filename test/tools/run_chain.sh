#!/bin/bash

[ -f ./test_chain.pid ] && kill `cat ./test_chain.pid`
#truffle develop --log &
node ./tools/testrpc/run.js &
echo $! > ./test_chain.pid
