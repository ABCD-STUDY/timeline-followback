<?php
  session_start();

  include($_SERVER["DOCUMENT_ROOT"]."/code/php/AC.php");
  $user_name = check_logged(); /// function checks if we are logged in
  $admin = false;

  if ($user_name == "") {
    // user is not logged in
    return;
  } else {
    $admin = true;
  }
  
  $permissions = list_permissions_for_user( $user_name );

  // find the first permission that corresponds to a site
  // Assumption here is that a user can only add assessment for the first site he has permissions for!
  $site = "";
  foreach ($permissions as $per) {
     $a = explode("Site", $per); // permissions should be structured as "Site<site name>"
     if (count($a) > 1) {
         $site = $a[1];
	     break;
     }
  }
  # todo, do this for all site permissions, not just the first one
  if ($site == "") {
     echo (json_encode ( array( "message" => "Error: no site assigned to this user" ) ) );
     return;
  }

  # use the user to lookup the correct token
  $tokens = json_decode(file_get_contents('tokens.json'),true);
  $keys = array_keys($tokens);
  $token = "";
  foreach($keys as $k) {
     if (strtolower($k) == strtolower($site)) {
       $token = $tokens[$k];
     }     
  }

  $data = array(
      'token' => $token,
      'content' => 'event',
      'format' => 'json',
      'returnFormat' => 'json'
  );
  $ch = curl_init();
  curl_setopt($ch, CURLOPT_URL, 'https://abcd-rc.ucsd.edu/redcap/api/');
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
  curl_setopt($ch, CURLOPT_VERBOSE, 0);
  curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
  curl_setopt($ch, CURLOPT_AUTOREFERER, true);
  curl_setopt($ch, CURLOPT_MAXREDIRS, 10);
  curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'POST');
  curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data, '', '&'));
  $output = curl_exec($ch);
  print $output;
  curl_close($ch);

?>
