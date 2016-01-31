<?php
  // TODO: add index number field to each scan in report view

  session_start(); /// initialize session, we will use session variables to store the subjid

  include($_SERVER["DOCUMENT_ROOT"]."/code/php/AC.php");
  $user_name = check_logged(); /// function checks if visitor is logged.

  if (!$user_name || $user_name == "") {
     echo (json_encode ( array( "message" => "no user name" ) ) );
     return; // nothing
  }

  $permissions = list_permissions_for_user( $user_name );

  // find the first permission that corresponds to a site
  // Assumption here is that a user can only add assessment for the first site he has permissions for!
  $site = "";
  foreach ($permissions as $per) {
     $a = explode("Site-", $per);

     if (count($a) > 0) {
        $site = $a[1];
	break;
     }
  }
  if ($site == "") {
     echo (json_encode ( array( "message" => "Error: no site assigned to this user" ) ) );
     return;
  }

  // Both the subject id and the visit (session) are used to make the assessment unique
  $subjid = "";
  $session = "";
  if (isset($_SESSION['subjid'])) {
     $subjid = $_SESSION['subjid'];
  } else {
     echo(json_encode ( array( "message" => "Error: no subject id assigned" ) ) );
     return;
  }
  if (isset($_SESSION['sessionid'])) {
     $session = $_SESSION['sessionid'];
  } else {
     echo(json_encode ( array( "message" => "Error: no session specified" ) ) );
     return;
  }

  // this events file needs to be saved here (should we add date here as well?)
  $events_file = $_SERVER['DOCUMENT_ROOT']."/applications/timeline-followback/data/" . $site . "/events_".$subjid."_".$session.".json";

  function loadEvents() {
     global $events_file;

     // parse permissions
     if (!file_exists($events_file)) {
        file_put_contents($events_file, json_encode( array( ) ));
     }
     if (!is_readable($events_file)) {
        echo ('error: cannot read file: '.$events_file);
        return;
     }
     $d = json_decode(file_get_contents($events_file), true);

     return $d;
  }

  function saveEvents( $events ) {
     global $events_file;

     // parse permissions
     if (!file_exists($events_file)) {
        echo ('error: events file does not exist');
        return;
     }
     if (!is_writable($events_file)) {
        echo ('Error: cannot write events file ('.$events_file.')');
        return;
     }
     // be more careful here, we need to write first to a new file, make sure that this
     // works and copy the result over to the pw_file
     $testfn = $events_file . '_test';
     file_put_contents($testfn, json_encode($events, JSON_PRETTY_PRINT));
     if (filesize($testfn) > 0) {
        // seems to have worked, now rename this file to pw_file
        rename($testfn, $events_file);
     } else {
        syslog(LOG_EMERG, 'ERROR: could not write file into '.$testfn);
     }
  }

  if (isset($_GET['action']))
    $action = $_GET['action'];
  else
    $action = null;

  if (isset($_GET['value']))
    $value = rawurldecode($_GET['value']);
  else
    $value = null;

  if (isset($_GET['value2']))
    $value2 = rawurldecode($_GET['value2']);
  else
    $value2 = null;

  if (isset($_GET['value3']))
    $value3 = rawurldecode($_GET['value3']);
  else
    $value3 = null;
  
  if (isset($_GET['value4']))
    $value4 = rawurldecode($_GET['value4']);
  else
    $value4 = null;

  if (isset($_GET['value5']))
    $value5 = rawurldecode($_GET['value5']);
  else
    $value5 = null;

  if (isset($_GET['value6']))
    $value6 = rawurldecode($_GET['value6']);
  else
    $value6 = null;

  if (isset($_GET['value7']))
    $value7 = rawurldecode($_GET['value7']);
  else
    $value7 = null;

  if (isset($_GET['value8']))
    $value8 = rawurldecode($_GET['value8']);
  else
    $value8 = null;

  if (isset($_GET['value9']))
    $value9 = rawurldecode($_GET['value9']);
  else
    $value9 = null;

  if (isset($_GET['start']))
    $start = rawurldecode($_GET['start']);
  else
    $start = null;

  if (isset($_GET['end']))
    $end = rawurldecode($_GET['end']);
  else
    $end = null;

  // create a new event
  if ($action == "create") { // TODO: do not create anything that is in the past
    //if (!check_role( "admin" )) {
    //   return;
    //}
    $e = loadEvents();
    $eid = uniqid();

    // remove this: $e[] = array('scantitle' => $value, 'start' => $value2, 'end' => $value3, 'project' => $project, 'user' => $user_name, 'eid' => $eid, 'noshow' => $value5, 'referrer' => $value6, 'amount' => $value7, 'protocol' => $value8, 'units' => $value9);
    $e[] = array('title' => $value, 'start' => $value2, 'end' => $value3, 'user' => $user_name, 'eid' => $eid, 'substance' => $value7, 'amount' => $value8, 'units' => $value9);
 
    saveEvents($e);

    echo (json_encode( array( 'message' => 'event added', 'eid' => $eid, "ok" => 1)));
    return;

  } else if ($action == "remove") { // TODO: do not remove anything that is in the past
    //if (!check_role( "admin" )) {
    //   return;
    //}
    $title       = $value;
    $start       = $value2;
    $end         = $value3;
    $eid         = $value4;

    $e = loadEvents();
    // identify the event just by the event id
    foreach ($e as $key => $event) {
      if ($event['eid'] == $eid) {
        // found the event, delete it now
        //echo("delete the event now\n");
        unset($e[$key]);
        saveEvents(array_values($e)); // this removes keys again

        // response
        echo(json_encode(array("message" => "event deleted", "ok" => 1)));
        return;
      }
    }

    echo(json_encode(array("message" => "event not found", "ok" => 0)));
    return;

  } else if ($action == "update") {
    //if (!check_role( "admin" )) {
    //   return;
    //}
    $title       = $value;
    $start       = $value2;
    $end         = $value3;
    $eid         = $value4;
    $substance   = $value7;
    $amount      = $value8;
    $units       = $value9;

    $e = loadEvents();
    // identify the event just by the event id
    foreach ($e as $key => &$event) {
      if ($event['eid'] == $eid) {
        // found the event, change it now
      	$event['title'] = $title;
        $event['start'] = $start;
      	$event['end']   = $end;
        $event['substance']   = $substance;
      	$event['amount']   = $amount;
      	$event['units']  = $units;

        //echo(json_encode(array("message" => "save changed events")));
        saveEvents(array_values($e)); // this removes keys from the array

        echo(json_encode(array("message" => "event changed right now", "ok" => 1)));
        return;
      }
    }

    echo(json_encode(array("message" => "event not found", "ok" => 0)));
    return;    
  } else if ( $start != null ) { // called by fullcalendar
    $e = loadEvents();

    $startdate = DateTime::createFromFormat('Y-m-d', $start);
    $enddate   = DateTime::createFromFormat('Y-m-d', $end);

    $events = [];
    foreach ($e as $key => $event) {
      $dateA = DateTime::createFromFormat(DateTime::ATOM, $event['start']);
      $dateB = DateTime::createFromFormat(DateTime::ATOM, $event['end']);

      if ( ($dateA >= $startdate && $dateA <= $enddate) ||
           ($dateB >= $startdate || $dateB <= $enddate)) {
        $event['title'] = $event['title'];
        $events[] = $event;
      }
    }
    echo(json_encode(array_values($events)));
  } else { // if we just list
    $e = loadEvents();
    echo(json_encode($e));
  }
?>
