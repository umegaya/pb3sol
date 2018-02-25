CONTAINER=umegaya/pb3sol
SOLIDITY_PLUGIN=/protoc/plugin/gen_sol.py

proto:
	docker run --rm -ti -v `pwd`/contracts/libs:/out -v `pwd`/proto:/in ${CONTAINER} \
		protoc -I/ -I/protoc/include --plugin=protoc-gen-sol=${SOLIDITY_PLUGIN} --sol_out=/out /in/TaskList.proto

shell:
	docker run --rm -ti -v `pwd`/contracts/libs:/out -v `pwd`/proto:/in -v `pwd`/../src/protoc:/protoc ${CONTAINER} bash