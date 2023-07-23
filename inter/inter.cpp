#include <fstream>
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include <cmath>

using namespace std;

int var_liste[512] = { 0 };
string var_name[512] = { "unset" };
int maxset = 0;
bool DEBUGPRINT = false;

void setvar(string name, int vall) {
	for (int i = 0; i <= maxset; i++) {
		if (var_name[i] == name) {
			if (DEBUGPRINT) {cout << "modification de: " << name << " = " << vall << endl; }
			var_liste[i] = vall;
			return;
		}
	}
	maxset++;
	if (DEBUGPRINT) {
		cout << "creation de: " << name << " = " << vall << endl;
	}
	var_name[maxset] = name;
	var_liste[maxset] = vall;
}

int getvar(string name) {
	for (int i = 0; i <= maxset; i++) {
		if (var_name[i] == name) {
			return var_liste[i];
		}
	}
	cout << "variable '" << name << "' non trouvée" << endl;
	return 0;
}

vector<string> split(string x, char delim = ' ')
{
	x += delim; //includes a delimiter at the end so last word is also read
	vector<string> splitted;
	string temp = "";
	for (int i = 0; i < x.length(); i++)
	{
		if (x[i] == delim)
		{
			splitted.push_back(temp); //store words in "splitted" vector
			temp = "";
			i++;
		}
		temp += x[i];
	}
	return splitted;
}

string readFile(const string& path) { // delftstack.com
	auto ss = ostringstream{};
	ifstream input_file(path);
	if (!input_file.is_open()) {
		cerr << "Impossible de lire le fichier - '"
			<< path << "'" << endl;
		exit(EXIT_FAILURE);
	}
	ss << input_file.rdbuf();
	return ss.str();
}

int calc(string calcul, int var1, int var2) {
	if (calcul == "+") {
		return var1 + var2;
	}
	else if (calcul == "-") {
		return var1 - var2;
	}
	else if (calcul == "*") {
		return var1 * var2;
	}
	else if (calcul == "/") {
		return var1 / var2;
	}
	else if (calcul == "^") {
		return pow(var1, var2);
	}
	else if (calcul == "%") {
		return var1 % var2;
	}
	else {
		cout << "calc: operateur inconnu: " << calcul << endl;
	}
	return 0;
}

int compar(string comparateur, string var1, string var2) {
	int a = getvar(var1);
	int b = getvar(var2);
	if (comparateur == "==" || comparateur == "=") {
		return a == b;
	}
	else if (comparateur == "!=") {
		return a != b;
	}
	else if (comparateur == ">") {
		return a > b;
	}
	else if (comparateur == "<") {
		return a < b;
	}
	else if (comparateur == ">=") {
		return a >= b;
	}
	else if (comparateur == "<=") {
		return a <= b;
	}
	else {
		cout << "Erreur dde comparaison: '" << comparateur << endl;
		return 0;
	}
}

int string_to_int(string texte) {
	stringstream intValue(texte);
	int number = 0;
	intValue >> number;
	return number;
}

void codeinloop(vector<string> code, string nom, int max);

string bcl_ctrl(vector<string> code, int i, string nom, int nb) {
	
	vector<string> codetoloop;

	for (int j = i + 1; j < code.size(); j++) {
		codetoloop.push_back(code[j]);
	}

	codeinloop(codetoloop, nom, nb);
	return nom;
}

void codeinloop(vector<string> code, string nom, int max) {
	if (DEBUGPRINT) {
		cout << "demarage de la boucle: " << nom << endl;
	}
	string sauter = "";
	for (int rep = 0; rep < max; rep++) {
		for (int i = 0; i < code.size(); i++) {
			string ligne = code[i];
			if (DEBUGPRINT) {
				cout << "[" << nom << "](" << rep << "~" << i << ")*** " << ligne << " ***" << endl;
			}
			
			vector<string> args = split(ligne, ' ');
			string mode = args[0];

			if (sauter == "" || (mode == "E" && args[1] == sauter)) {
				if (sauter != "") {
					sauter = "";
				}
				if (mode == "") {
					continue;
				}

				else if (mode == "V") {
					setvar(args[1], string_to_int(args[2]));
				}

				else if (mode == "A") {
					cout << getvar(args[1]);
					if (DEBUGPRINT) {cout << "\n";}
				}

				else if (mode == "D") {
					if (args[1] == "off") {
						DEBUGPRINT = false;
					}
					else {
						DEBUGPRINT = true;
					}
				}

				else if (mode == "H") {
					setvar(args[1], getvar(args[2]));
				}

				else if (mode == "L") {
					sauter = bcl_ctrl(code, i, args[1], getvar(args[2]));
				}

				else if (mode == "E") {
					if (args[1] == nom) {
						if (DEBUGPRINT) {
							cout << "arret de la boucle '" << nom << "'" << endl;
						}
						break;
					}
				}

				else if (mode == "X") {
					if (getvar(args[2]) == 1) {
						sauter = bcl_ctrl(code, i, args[1], 1);
					}
					else {
						sauter = args[1];
						if (DEBUGPRINT) {
							cout << "condition non remplie: " << sauter << endl;
						}
					}
				}

				else if (mode == "C") {
					setvar(args[1], calc(args[3], getvar(args[2]), getvar(args[4])));
				}

				else if (mode == "B") {
					setvar(args[1], compar(args[3], args[2], args[4]));
				}

				else if (mode == "Z") {
					break;
				}

				else if (mode == "S") {
					if (args.size() == 1) {
						cout << endl;
					}
					else {
						cout << args[1];
					}
					if (DEBUGPRINT) { cout << endl; }
				}

			}
		}
	}
}

void start(string code) {
	while (code.find_first_of("\n") != string::npos) {
		code.replace(code.find("\n"), 1, ";");
	}
	vector<string> sortie = split(code, ';');
	codeinloop(sortie, "main", 1);
}

int main() {
	string filename("code.kea");
	string file_contents = readFile(filename);
	start(file_contents);

	return EXIT_SUCCESS;
}