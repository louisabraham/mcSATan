all: simple
	
simple:
	python3 -m mcSATan.cnf tests/simple_v3_c2.cnf --debug=10

php77:
	./profile.sh tests/php77.cnf

