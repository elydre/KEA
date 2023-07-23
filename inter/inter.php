<?php
/*    _             _
 ___ | | _   _   __| | _ __   ___
/ _ \| || | | | / _` || '__| / _ |
| __/| || |_| || (_| || |   |  __/
\___||_| \__, | \__,_||_|    \___|
          |___/
___________________________________

- codé en : UTF-8
- langage : php
- GitHub  : github.com/elydre
- Licence : MIT
*/

$version = "1.2.21";

function debug_print($texte, $blue = false){
    global $DEBUG;
    if ($DEBUG) {
        if ($blue) {
            echo "\e[0;1;30m$texte\e[0m";
        } else {
            echo $texte;
        }
    }
}

function user_input($var, $ACTIVE) {
    setvar($var, readline(), $ACTIVE);
}

function debug_print_all() {
    echo "\nVARIABLES:\n";
    global $VAR;
    foreach ($VAR as $key => $value) {
        echo "- $key = $value\n";
    }
    echo "\nFONCTIONS:\n";
    global $FUNCTIONS;
    foreach ($FUNCTIONS as $key => $value) {
        echo "- $key ~ i$value[1]\n";
    }
}

function compar($comparateur, $a, $b) {
    switch($comparateur) {
        case "==":
            return $a == $b;
        case "=":
            return $a == $b;
        case "!=":
            return $a != $b;
        case ">":
            return $a > $b;
        case "<":
            return $a < $b;
        case ">=":
            return $a >= $b;
        case "<=":
            return $a <= $b;
        default:
            echo "Erreur de comparaison : '$comparateur' \n";
    }
}

function calc($calcul, $var1, $var2) {
    switch($calcul) {
        case "+":
            return $var1 + $var2;
        case "-":
            return $var1 - $var2;
        case "*":
            return $var1 * $var2;
        case "^":
            return $var1 ** $var2;
        case "**":
            return $var1 ** $var2;
        case "/":
            return $var1 / $var2;
        case "%":
            return $var1 % $var2;
        default:
            echo "Erreur de calcul : '$calcul' \n";
    }
}

function makename($name, $active) {
    if ($name[0] != "!") {
        return $active . "_" . $name;
    }
    return $name;
}

function getvar($name, $active) {
    global $VAR;
    $name = makename($name, $active);
    if (isset($VAR[$name])) {
        return $VAR[$name];
    }
    echo "Variable $name non trouvée\n";
    return "";
}

function setvar($name, $valeur, $active) {
    global $VAR;
    $name = makename($name, $active);
    debug_print("$active → V '$name' = '$valeur'\n");
    $VAR[$name] = $valeur;
}

function setsauter($valeur, $nom) {
    debug_print("$nom → sauter = '$valeur'\n");
    return $valeur;
}

function add_sharp($code) {
    $to_add = array();
    $names  = array();
    for ($i = 0; $i <= sizeof($code); $i++) {
        $args = explode(" ", $code[$i]);
        if($args[0] != "#") {
            break;
        }
        else if ($args[1] = "add") {
            unset($code[0]);
            array_push($to_add, explode("\n", str_replace("\r", "", str_replace(";", "\n", file_get_contents($args[2])))));
            array_push($names, $args[2]);
        }
    }
    foreach ($to_add as $k => $e) {
        $code = array_merge($e, $code);
        echo "merge de '$names[$k]' avec succès!\n";
    }

    return $code;
}

function start ($code) {
    global $VAR, $DEBUG, $FUNCTIONS;
    $DEBUG = false;
    $VAR = [];
    $FUNCTIONS = [];

    $code = str_replace(";", "\n", $code);
    $code = str_replace("\r", "", $code);
    $code = explode("\n", $code);

    $code = add_sharp($code);

    codeinloop($code, "main", 1, "main");
}

function start_fonction($args, $fonc_name) {
    global $FUNCTIONS;

    $fonction = $args[1];

    if (isset($FUNCTIONS[$fonction])) {

        $fonc_code =    $FUNCTIONS[$fonction][0];
        $oldi =         $FUNCTIONS[$fonction][1];
        $in_fonc_args = $FUNCTIONS[$fonction][2];

        if (isset($args[2])) {
            $out_args = explode("&", $args[2]);
        } else {
            $out_args = [];
        }

        for ($j = 0; $j < sizeof($in_fonc_args); $j++) {
            if(isset($out_args[$j])) {
                setvar($in_fonc_args[$j], getvar($out_args[$j], $fonc_name), $args[1]);
                debug_print("création de la variable '$in_fonc_args[$j]' = '". getvar($out_args[$j], $fonc_name) ."' dans la fonction '$args[1]'\n");
            }
            else {
                echo "Erreur: fonction '$args[1]' : argument $j non défini\n";
            }
        }
        return bcl_ctrl($fonc_code, $oldi, $args[1], 1, $args[1])[1];
    }
    echo "Fonction $fonction non trouvée\n";
}

function save_fonction($name, $code, $i, $args) {
    global $FUNCTIONS;
    $FUNCTIONS[$name] = [$code, $i, $args];
}

function bcl_ctrl($code, $i, $nom, $nb, $fonc_name){
    $codetoloop = array();
                    
    for ($j = $i+1; $j < sizeof($code); $j++) {
        array_push($codetoloop, $code[$j]);
    }
    
    return codeinloop($codetoloop, $nom, $nb, $fonc_name);
}

function codeinloop($code, $nom ,$max, $fonc_name) {
    global $DEBUG, $FUNCTIONS;
    debug_print("DEMARAGE DE LA BOUCLE '$nom'\n");
    $sauter = setsauter("", $nom);
    $dobreak = 0;
    for ($rep = 0; $rep < $max; $rep++) {
        for ($i = 0; $i < sizeof($code); $i++) {
            $ligne = $code[$i];
            $ligne = trim($ligne);

            debug_print("[$fonc_name | $nom]($rep~$i) *** $ligne ***\n", true);

            $args = explode(" ", $ligne);
            $mode = $args[0];
            
            if($sauter == "" || ($mode == "E" && $args[1] == $sauter)){
                if ($sauter != "") {
                    $sauter = setsauter("", $nom);
                }

                if($mode == "") {
                    continue;
                }

                else if ($mode == "V"){
                    $var = $args[1];
                    $val = $args[2];
                    setvar($var, $val, $fonc_name);
                }

                else if ($mode == "L") {
                    $dobreak = bcl_ctrl($code, $i, $args[1], getvar($args[2], $fonc_name), $fonc_name)[0];
                    $sauter = setsauter($args[1], $nom);
                }

                else if ($mode == "E") {
                    if ($args[1] == $nom) {
                        debug_print("ARRET DE LA BOUCLE '$nom'");
                        if (isset($args[2])) {
                            debug_print(" PAR RETURN\n");
                            return [0, getvar($args[2], $fonc_name)];
                        }
                        debug_print(" PAR BREAK\n");
                        break;
                    }
                }

                else if ($mode == "C"){
                    $result = calc($args[3], getvar($args[2], $fonc_name), getvar($args[4], $fonc_name));
                    setvar($args[1], $result, $fonc_name);
                }

                else if ($mode == "Z") {
                    $dobreak = 1;
                    if (isset($args[1])) {
                        $dobreak = getvar($args[1], $fonc_name);
                    }
                }

                else if ($mode == "B") {
                    setvar($args[1], compar($args[3], getvar($args[2], $fonc_name), getvar($args[4], $fonc_name)), $fonc_name);
                }

                else if ($mode == "H") {
                    setvar($args[1], getvar($args[2], $fonc_name), $fonc_name);
                }

                else if ($mode == "F"){
                    $fonc_args = array();
                    if (isset($args[2])) {
                        $fonc_args = explode("&", $args[2]);
                    }
                    save_fonction($args[1], $code, $i, $fonc_args);
                    $sauter = setsauter($args[1], $nom);
                }

                else if ($mode == "T"){
                    $sortie = start_fonction($args, $fonc_name);
                    if (isset($args[3])) {
                        setvar($args[3], $sortie, $fonc_name);
                    }
                }

                else if ($mode == "D") {
                    if ($args[1] == "on") {
                        $DEBUG = true;
                    }
                    else if ($args[1] == "off") {
                        $DEBUG = false;
                    }
                    else {
                        debug_print_all();
                    }
                }

                else if ($mode == "R"){
                    $rand = rand(0, getvar($args[2], $fonc_name));
                    setvar($args[1], $rand, $nom);
                }

                else if ($mode == "X") {
                    if (getvar($args[2], $fonc_name) == true) {
                        $dobreak = bcl_ctrl($code, $i, $args[1], 1, $fonc_name)[0];
                        $sauter = setsauter($args[1], $nom);
                    }
                    else {
                        $sauter = setsauter($args[1], $nom);
                        debug_print("condition non remplie: $sauter\n");
                    }
                }

                else if ($mode == "S") {
                    if (empty($args[1])) {
                        echo "\n";
                    }
                    else {
                        echo "\e[0;0;33m". str_replace("_", " ", $args[1]) . "\e[0m";
                    }
                    if ($DEBUG) {echo "\n";}
                }

                else if ($mode == "I") {
                    user_input($args[1], $fonc_name);
                }

                else if ($mode == "A") {
                    echo "\e[0;1;33m". str_replace("_", " ", getvar($args[1], $fonc_name)). "\e[0m";
                    if ($DEBUG) {echo "\n";}
                }

                else if ($mode =! "//") {
                    echo "Erreur de mode: $mode\n";
                }
            }
            else {
                debug_print("$nom → passer '$ligne'\n");
            }
            if ($dobreak > 0) {
                return [$dobreak - 1, 0];
            }
        }
    }
    return [0, 0];
}

if (isset($argv[1])) {
    $code = file_get_contents($argv[1]);
    start($code);
}
else {
    echo "Erreur: pas de fichier\n";
}