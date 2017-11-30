<?php

  session_start(); /// initialize session, we will use session variables to store the subjid

  $access_control_file = $_SERVER["DOCUMENT_ROOT"]."/code/php/AC.php";
  $stand_alone = true;
  if (file_exists($access_control_file)) {
    $stand_alone = false;
    include($access_control_file);
    $user_name = check_logged(); /// function checks if user is logged in

    if (!$user_name || $user_name == "") {
       echo (json_encode ( array( "message" => "no user name" ) ) );
       return; // nothing
    }

    $permissions = list_permissions_for_user( $user_name );

    // find the first permission that corresponds to a site
    // Assumption here is that a user can only add assessment for the first site he has permissions for!
    $site = "";
    foreach ($permissions as $per) {
       $a = explode("Site", $per); // permissions should be structured as "Site<site name>"

       if (count($a) > 0) {
          $site = $a[1];
  	  break;
       }
    }
    if ($site == "") {
       echo (json_encode ( array( "message" => "Error: no site assigned to this user" ) ) );
       return;
    }
  } else {
    $user_name = "anonymous";
    $site = "anonymous";
  }
  // Both the subject id and the visit (session) are used to make the assessment unique
   $subjid = "";
   $sessionid = "";
   $active_substances = array();
   if ( isset($_SESSION['ABCD']) && isset($_SESSION['ABCD']['timeline-followback']) ) {
      if (isset($_SESSION['ABCD']['timeline-followback']['subjid'])) {  
         $subjid  = $_SESSION['ABCD']['timeline-followback']['subjid'];
      }
      if (isset($_SESSION['ABCD']['timeline-followback']['sessionid'])) {
         $sessionid  = $_SESSION['ABCD']['timeline-followback']['sessionid'];
      }      
      if (isset($_SESSION['ABCD']['timeline-followback']['act_subst'])) {
         $active_substances = json_decode(rawurldecode($_SESSION['ABCD']['timeline-followback']['act_subst']), true);
      }
   }

   if ($subjid == "") {
     // This would trip the calendar call, it does not expect a string to be returned - would produce a alert
     //echo(json_encode ( array( "message" => "Error: no subject id assigned" ) ) );
     return;
   }
   if ($sessionid == "") {
     echo(json_encode ( array( "message" => "Error: no session specified" ) ) );
     return;
   }

   // this event will be saved at this location
   if ($stand_alone) {
      $events_file = "../../data/" . $site . "/events_".$subjid."_".$sessionid.".json";
   } else {
      $events_file = $_SERVER['DOCUMENT_ROOT']."/applications/timeline-followback/data/" . $site . "/events_".$subjid."_".$sessionid.".json";
   }

   // check if the site directory exits, otherwise create it
   if ($stand_alone) {
      $dd = "../../data/" . $site;
   } else {
      $dd = $_SERVER['DOCUMENT_ROOT']."/applications/timeline-followback/data/" . $site;
   }
   if(!file_exists($dd)) {
      mkdir($dd,0777);
   }

  function loadEvents() {
     global $events_file;

     // parse permissions
     if (!file_exists($events_file)) {
        file_put_contents($events_file, json_encode( array( "data" => [] ) ));
	if (!file_exists($events_file)) {
          syslog(LOG_EMERG, "ERROR: could not create initial session file at: ".$events_file);
          return;
	}		
     }
     if (!is_readable($events_file)) {
        echo ("error: cannot read file: ".$events_file);
        return;
     }
     $d = json_decode(file_get_contents($events_file), true);

     return $d;
  }

  function saveEvents( $events ) {
     global $events_file;

     // parse permissions
     if (!file_exists($events_file)) {
        echo ("error: events file does not exist");
        return;
     }
     if (!is_writable($events_file)) {
        echo ("Error: cannot write events file (".$events_file.")");
        return;
     }
     // be more careful here, we need to write first to a new file, make sure that this
     // works and copy the result over to the pw_file (prevents problems in case the harddrive is full - 
     // would otherwise remove the content of the file upon writing)
     $testfn = $events_file . "_test";
     file_put_contents($testfn, json_encode($events, JSON_PRETTY_PRINT));
     if (filesize($testfn) > 0) {
        // seems to have worked, now rename this file to pw_file
        rename($testfn, $events_file);
     } else {
        syslog(LOG_EMERG, "ERROR: could not write file into ".$testfn);
     }
  }

  if (isset($_GET["action"]))
    $action = $_GET["action"];
  else
    $action = null;

  // check if this event can be saved
  if ($action == "test") {
     return; 
  }

  if (isset($_GET["start"]))
    $start = rawurldecode($_GET["start"]);
  else
    $start = null;

  if (isset($_GET["end"]))
    $end = rawurldecode($_GET["end"]);
  else
    $end = null;

  // create a new event
  if ($action == "create") {
    $e = loadEvents();
    $eid = uniqid();

    $ar = array( "eid" => $eid );
    foreach ($_GET as $key => $value) {
       if ($key == "eid") { // don't allow event id to be overwritten
          continue;
       }
       if ($key == "action") {
          continue;
       }
       $ar[$key] = rawurldecode($value);
    }

    $e["data"][] = $ar;
    $e["active_substances"] = $active_substances;
    // array("title" => $value, "start" => $value2, "end" => $value3, "user" => $user_name, "eid" => $eid, "substance" => $value7, "amount" => $value8, "units" => $value9);
 
    saveEvents($e);

    echo (json_encode( array( "message" => "event added", "eid" => $eid, "ok" => 1)));
    return;

  } else if ($action == "remove") { // TODO: do not remove anything that is in the past
    $ar = array();
    foreach ($_GET as $key => $value) {
       if ($key == "action") {
          continue;
       }
       $ar[$key] = rawurldecode($value);
    }
    $eid = $ar['eid'];

    $e = loadEvents();
    // identify the event just by the event id
    foreach ($e["data"] as $key => $event) {
      if ($event["eid"] == $eid) {
        unset($e["data"][$key]);
        $e["data"] = array_values($e["data"]); // this removes keys again
        saveEvents($e); 

        // response
        echo(json_encode(array("message" => "event deleted", "ok" => 1)));
        return;
      }
    }

    echo(json_encode(array("message" => "event not found", "ok" => 0)));
    return;

  } else if ($action == "update") {
 
    $eid = "";
    if (isset($_GET['eid'])) {
      $eid         = $_GET['eid'];
    } else {
      echo(json_encode(array("message" => "Error: event id not found", "ok" => 0)));
      return;
    }

    $e = loadEvents();
    // identify the event just by the event id
    foreach ($e["data"] as $key => &$event) {
      if ($event["eid"] == $eid) {
        // found the event, change it now
        foreach ($_GET as $key => $value) {
   	   if ($key == "eid") {
	      continue;
	   }
	   if ($key == "action") {
	      continue;
	   }
	   $event[$key] = rawurldecode($value); // copy or update value
        }

        $e["data"] = array_values($e["data"]); // this removes keys from the array
	if (count($active_substances) > 0) {
           $e["active_substances"] = $active_substances;
        }
        saveEvents($e); 

        echo(json_encode(array("message" => "event changed right now", "ok" => 1)));
        return;
      }
    }

    echo(json_encode(array("message" => "event not found", "ok" => 0)));
    return;
  } else if ( $action == "mark" ) {

    $e = loadEvents();
    $ar = array( 'date' => date(DATE_ATOM) );
    foreach ($_GET as $key => $value) {
       if ($key == "eid") {
          continue;
       }
       if ($key == "action") {
          continue;
       }
       if ($key == "date") {
          continue; // ignore dates we don't set ourselfs
       }
       $ar[$key] = $value;
    }

    $e['status'][] = $ar;

    saveEvents($e);
    echo(json_encode(array( "message" => "stored mark", "ok" => 1)));
  } else if ( $start != null ) { // called by fullcalendar
    $e = loadEvents();

    $startdate = DateTime::createFromFormat("Y-m-d", $start);
    $enddate   = DateTime::createFromFormat("Y-m-d", $end);

    $events = [];
    foreach ($e["data"] as $key => $event) {
      $dateA = DateTime::createFromFormat(DateTime::ATOM, $event["start"]);
      $dateB = DateTime::createFromFormat(DateTime::ATOM, $event["end"]);

      if ( ($dateA >= $startdate && $dateA <= $enddate) ||
           ($dateB >= $startdate || $dateB <= $enddate)) {
        $events[] = $event;
      }
    }
    echo(json_encode(array_values($events)));
  } else { // if we just list
    $e = loadEvents();
    echo(json_encode($e["data"]));
  }
?>
