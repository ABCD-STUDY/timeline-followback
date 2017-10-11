<?php

  // store session variables as $_SESSION['ABCD'] = [ "TaskName" => [ "key" => "value", ] ]
  // expected argument is $_GET['task'] the name of the task

  session_start();

  $access_control_file = $_SERVER["DOCUMENT_ROOT"]."/code/php/AC.php";
  $stand_alone = false;
  if (file_exists($access_control_file)) {
    $stand_alone = true;
    include($access_control_file);
    $user_name = check_logged(); /// function checks if visitor is logged.
  } else {
    $user_name = "anonymous";
  }
  // assume that we need subjectid, sessionid, and task
  $ar = array();
  if (isset($_SESSION['ABCD'])) {
     $ar = $_SESSION['ABCD'];
  }

  $task = "";
  if (isset($_GET['task'])) {
     $task = $_GET['task'];
  } else {
     echo ("ERROR: no task specified, cannot do anything");
     return;
  }

  // all values we have to store (could be subjid, sessionid, etc.)
  $vals = array();
  foreach($_GET as $key => $value) {
     if ($key == "task") {
         continue;
     }
     $vals[$key] = $value;
  }
  if (!array_key_exists($task, $ar)) {
     $ar[$task] = array();
  }
  $ar[$task] = array_merge($ar[$task], $vals);

  $_SESSION['ABCD'] = $ar;
?>