<?php
  $contacts_file = $_SERVER['DOCUMENT_ROOT']."/applications/timeline-followback/data/sessions.json";

  date_default_timezone_set('America/Los_Angeles');
  session_start(); /// initialize session
  include($_SERVER['DOCUMENT_ROOT']."/code/php/AC.php");
  $user_name = check_logged(); /// function checks if visitor is logged.
  if (!$user_name)
     return; // nothing
  /*
  if (!check_permission("can-order")) {
     echo ("{ \"message\": \"no permission to order for this user\" }");
     return; // do nothing
  }
  */

  function loadContacts() {
     global $contacts_file;

     // parse permissions
     if (!file_exists($contacts_file)) {
        echo ('error: contacts file does not exist');
        return;
     }
     if (!is_readable($contacts_file)) {
        echo ('error: cannot read file '.$contacts_file.'...');
        return;
     }
     $d = json_decode(file_get_contents($contacts_file), true);
     if (!is_array($d)) {
        echo('error: could not parse the ref file, contained: '.$d.'\n');
     }
     return $d;
  }

  function saveContacts( $contacts ) {
    global $contacts_file;

     // parse permissions
     if (!file_exists($contacts_file)) {
        echo ('error: notes file '.$contacts_file.' does not exist');
        return;
     }
     if (!is_writable($contacts_file)) {
        echo ('error: cannot write projects file ('.$contacts_file.')');
        return;
     }

     // lets sort the contacts alphabetically first
     //sort($contacts);

     //echo ("{ \"message\": \"save these values: " . join($contacts) . "\"}");

     // be more careful here, we need to write first to a new file, make sure that this
     // works and copy the result over to the pw_file
     $testfn = $contacts_file . '_test';
     file_put_contents($testfn, json_encode($contacts, JSON_PRETTY_PRINT));
     if (filesize($testfn) > 0) {
        // seems to have worked, now rename this file to pw_file
        rename($testfn, $contacts_file);
     } else {
        syslog(LOG_EMERG, 'error: could not write file into '.$testfn);
     }
  }

  function addContact( $id, $sessionID, $userName, $siteID, $status ) {
    $d = loadContacts();
    $now = date("F_j_Y_g:i_a");
    // do not store PII in the database. replace PII with NA string for now
    array_push($d, array( 'date' => $now, 'id' => $id, 'sessionID' => $sessionID, 'userName' => $userName, 'siteID' => $siteID, 'status' => $status ) );
    saveContacts($d);
    return $id;
  }

  function changeContact( $id, $sessionID, $userName, $siteID, $status ) {
     $d = loadContacts();
     foreach ( $d as &$prot ) {
        if ($prot['id'] == $id ) {
	   // found what we are looking for, replace this entry with the updated one
     //$prot['date'] = time(); // time last changed
     $prot['date'] = date("F_j_Y_g:i_a"); // time last changed
     $prot['sessionID'] = $sessionID;
	   $prot['userName'] = $userName;
     $prot['siteID'] = $siteID;
     $prot['status'] = $status;
	   break;
        }
     }
     saveContacts($d);
  }
  
  function removeContact( $id ) {
     $d = loadContacts();
     $found = 0;
     foreach ($d as $key => $ds ) {
        if ( $ds['id'] == $id ) {
           unset($d[$key]);
	   $found = $found + 1;
        }
     }
     if ($found == 1) {
       saveContacts(array_values($d));
     }
     return $found;
  }

  if (isset($_GET['action']))
    $action = $_GET['action'];
  else
    $action = null;

  if (isset($_GET['id']))
    $id = $_GET['id'];
  else
    $id = null;

  if (isset($_GET['sessionID']))
    $sessionID = $_GET['sessionID'];
  else
    $sessionID = null;

  if (isset($_GET['userName']))
    $userName = $_GET['userName'];
  else
    $userName = null;

  if (isset($_GET['siteID']))
    $siteID = $_GET['siteID'];
  else
    $siteID = null;

  if (isset($_GET['status']))
    $status = $_GET['status'];
  else
    $status = null;

  if ($action == "create") {
    $id = addContact( $id, $sessionID, $userName, $siteID, $status ); 
    echo ("{ \"id\": ".$id."}");
    return;
  } else if ($action == "remove") {
    $num = removeContact( $id );
    echo ("{ \"num\": ".$num."}");
    return;  
  } else if ($action == "change") {  
    changeContact( $id, $sessionID, $userName, $siteID, $status );
    echo ("{ \"message\": \"done\" }");
    return;  
  } else if ($action == "load") {  
    $d = loadContacts();
    echo(json_encode( $d ));
    return;
  } else {
    return;
  }
 ?>
 