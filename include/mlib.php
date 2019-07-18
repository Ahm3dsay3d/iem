<?php
//   mlib.php
// Library of functions

// Make sure a page is HTTPS when called
function force_https(){
  if (empty($_SERVER["HTTPS"]) || $_SERVER["HTTPS"] !== "on"){
    header("Location: https://" . $_SERVER["HTTP_HOST"] . $_SERVER["REQUEST_URI"]);
    exit();
  }
}

//________________________________________________________
function aSortBySecondIndex($multiArray, $secondIndex, $sorder="asc") {
    reset($multiArray);
    if (sizeof($multiArray) == 0){
        return array();
    }
    while (list($firstIndex, ) = each($multiArray))
        $indexMap[$firstIndex] = $multiArray[$firstIndex][$secondIndex];
        if ($sorder == "asc")
            asort($indexMap);
            else
                arsort($indexMap);
                while (list($firstIndex, ) = each($indexMap))
                    $sortedArray[$firstIndex] = $multiArray[$firstIndex];
                    return $sortedArray;
}

//_____________________________________________________________
function c2f($myC){
  if ($myC == ""){
    return "";
  }
  return round( ((9.00/5.00) * $myC + 32.00 ), 2);

} // End of function c2f()

//_____________________________________________________________
function f2c($tmpf){
	if ($tmpf == null) return null;
  return round( ((5.00/9.00) * ((float)$tmpf - 32.00) ), 2);

} // End of function f2c()


//______________________________________________________________
function dwpf($tmpf, $relh){
 $tmpk = 273.15 + (5.00/9.00 * ($tmpf - 32.00));
 $dwpk = $tmpk / (1 + 0.000425 * $tmpk * - (log10($relh/100)));
 return ($dwpk - 273.15) * 9.00/5.00 + 32 ;
}


//______________________________________________________________
// /home/nawips/nawips56.e.1/gempak/source/gemlib/pr/prvapr.f
// /home/nawips/nawips56.e.1/gempak/source/gemlib/pr/prrelh.f
function relh($tmpc, $dwpc){
	if ($tmpc == null || $dwpc == null) return null;
  $e  = 6.112 * exp( (17.67 * (float)$dwpc) / ((float)$dwpc + 243.5));
  $es  = 6.112 * exp( (17.67 * (float)$tmpc) / ((float)$tmpc + 243.5));
  $relh = ( $e / $es ) * 100.00;
  return round($relh,0);
}


function drct2txt($dir)
{
  $dir = intval($dir);
  if ($dir >= 350 || $dir < 13)  return "N";
  else if ($dir >= 13 && $dir < 35) return "NNE";
  else if ($dir >= 35 && $dir < 57) return "NE";
  else if ($dir >= 57 && $dir < 80) return "ENE";
  else if ($dir >= 80 && $dir < 102) return "E";
  else if ($dir >= 102 && $dir < 127) return "ESE";
  else if ($dir >= 127 && $dir < 143) return "SE";
  else if ($dir >= 143 && $dir < 166) return "SSE";
  else if ($dir >= 166 && $dir < 190) return "S";
  else if ($dir >= 190 && $dir < 215) return "SSW";
  else if ($dir >= 215 && $dir < 237) return "SW";
  else if ($dir >= 237 && $dir < 260) return "WSW";
  else if ($dir >= 260 && $dir < 281) return "W";
  else if ($dir >= 281 && $dir < 304) return "WNW";
  else if ($dir >= 304 && $dir < 324) return "NW";
  else if ($dir >= 324 && $dir < 350) return "NNW";
  return "";
}
?>