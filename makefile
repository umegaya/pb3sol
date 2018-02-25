image:
	make -C src image

tsh:
	make -C test shell

.PHONY: test
test:
	make -C test run