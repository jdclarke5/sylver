# sylver

Fun with Conway's game of Sylver Coinage.

***[under development]***

## Setup

Install the package and required dependencies with the following command.

```sh
pip install .
```

Some modules require additional packages. For example the `tree` module and particular `backend` modules. The user can install these as per their use case. To plot (small) trees the graphviz package should be installed on your OS, e.g.

```sh
sudo apt install graphviz
sudo apt install libgraphviz-dev
pip install pygraphviz
```

### Optional

## Web Application

Install `nodejs` and `npm`. 

```sh
sudo apt install nodejs npm
```

Install the node modules needed for the web application.

```sh
cd app
npm install
```

> Note: When installing any new node modules make sure to run with `--save-dev` or `--save-prod` to keep the package.json up to date.

Run the Flask RESTful API server.

```sh
export PYTHONPATH=..
export FLASK_APP=server.py
export FLASK_ENV=development
flask run
```

The API exposes a single endpoint: 

`GET` /api/get

Parameters:
- `input` (\[int\]): Comma-separated array of non-negative integers to use as position seeds.
- `length` (int, optional): Length of bitarray to use.
- `children` (bool, optional): Whether to include properties of children in response, keyed on response.

Sample response:

```json
{
	"frobenius": 79,
	"gcd": 1,
	"generators": [
		9,
		11
	],
	"genus": 40,
	"irreducible": "s",
	"multiplicity": 9,
	"name": "{9, 11}",
	"status": "N",
	"bitarray": [
		true,
		false,
        false,
        ...
	],
	"children": {
		"1": {
			"frobenius": 0,
			"gcd": 1,
			"generators": [
				1
			],
			"genus": 0,
			"irreducible": "p",
			"multiplicity": 1,
			"name": "{1}",
			"status": "N"
        },
        ...
	}
}
```

If the status of the requested position is unknown (not quickly solvable or stored in the backend), the server spawns a separate process to solve for that position. After some time, if the position is solvable, then resending the request will fetch a known position status. The user may also see the statuses of children get updated.

Run the web server (proxies to API server).

```sh
npm run serve
```

Navigate to [http://localhost:9000](http://localhost:9000).

#### PostgreSQL backend

sudo apt install postgresql postgresql-contrib

## Known

{1}: N
{2}: N [3]
{3}: N [2]
{4}: N [6]
{5}: P (prime)
{6}: N [4, 9]
{7}: P (prime)
{8}: N [12, 14, ?]
{9}: N [6]
{10}: N [5, 26, ?]
{11}: P (prime)
{12}: N [8]
{13}: P (prime)
{14}: N [7]
{15}: N [5]
{16}: ?? expect to be N but need to find the P position!!

Approach to solve {16}:
- Understand how to prove {8} is P: {8, 10, 22} is P and {8, 12, 8n+2, 8n+6} is P
- Understand how to prove {8, 14} is P (short)
- Profit

Some g=2 positions to try:
- [2] (N): No sols above 3
- [4, 6] (P): No sols above 2
- [8, 10, 12, 16] (P)
- [8, 12, 18, 22] (P)
- [6, 44, 82] (N) : (4, 5993171)

## Notes

- Suspect {10, 14, 26} is P... but apparently {10, 14} is P
