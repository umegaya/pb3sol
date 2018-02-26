CONTAINER=umegaya/pb3sol
SOLIDITY_PLUGIN=/protoc/plugin/gen_sol.py

define soliditize
docker run --rm -ti -v `pwd`/contracts/libs/pb:/out -v `pwd`/proto:/in -v `pwd`/../src/protoc:/protoc ${CONTAINER} \
	protoc -I/ -I/protoc/include --plugin=protoc-gen-sol=${SOLIDITY_PLUGIN} --sol_out=$2 $1
endef

.PHONY: proto
proto:
	$(call soliditize,/in/TaskList.proto,"gen_runtime=True:/out")

test_proto: proto
	sed -e 's/sfixed32 f4 = 5;/sfixed32 f4 = 5;.solidity.uint256 new_id = 6;/g' proto/TaskList.proto > proto/TaskList2.proto
	$(call soliditize,/in/TaskList2.proto,"/out")

shell:
	docker run --rm -ti -v `pwd`/contracts/libs:/out -v `pwd`/proto:/in -v `pwd`/../src/protoc:/protoc ${CONTAINER} bash

run: test_proto
	truffle test
