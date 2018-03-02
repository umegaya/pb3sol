image:
	make -C src image

tsh:
	docker run --rm -ti -v `pwd`:/test umegaya/pb3sol_test bash

test_setup:
	cd src/soltype-pb && npm install
	cd test && npm install

test_on_host:
	make -C test run CONTAINER_RUNARG="" INPUT_DIR=`pwd`/test/proto OUTPUT_DIR=`pwd`/test/contracts/libs/pb

test_image:
	make -C test image
