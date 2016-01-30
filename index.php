<?php
  session_start();

  include($_SERVER["DOCUMENT_ROOT"]."/code/php/AC.php");
  $user_name = check_logged(); /// function checks if visitor is logged.
  $admin = false;

  if ($user_name == "") {
    // user is not logged in

  } else {
    $admin = true;
    echo('<script type="text/javascript"> user_name = "'.$user_name.'"; </script>'."\n");
    echo('<script type="text/javascript"> admin = '.($admin?"true":"false").'; </script>'."\n");
  }
   // if there is a running session it would have the follow information
   $subjid  = $_SESSION['subjid'];
   $session = $_SESSION['sessionid'];
   echo('<script type="text/javascript"> subjid = "'.$subjid.'"; </script>'."\n");
   echo('<script type="text/javascript"> session = "'.$session.'"; </script>'."\n");
?>

<!DOCTYPE html>
<html lang="en">

<head>

  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="">
  <meta name="author" content="">

  <title>Timeline Followback</title>

  <!-- Bootstrap Core CSS -->
  <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">

  <!-- Custom CSS -->
  <!-- required for the date and time pickers -->
  <link href="css/bootstrap-datetimepicker.css" rel="stylesheet" type="text/css">

  <link rel='stylesheet' href='//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.6.0/fullcalendar.min.css' />
  <!-- media="print" is required to display the fullcalendar header buttons -->
  <link rel='stylesheet' media='print' href='//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.6.0/fullcalendar.print.css' />

  <link rel="stylesheet" href="css/style.css">

</head>

<body>

  <nav class="navbar navbar-default">
  <div class="container-fluid">
    <!-- Brand and toggle get grouped for better mobile display -->
    <div class="navbar-header">
      <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="#">Timeline Followback</a>
    </div>

    <!-- Collect the nav links, forms, and other content for toggling -->
    <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
      <ul class="nav navbar-nav">
        <li class="active"><a href="/index.php" title="Back to report page">Report</a></li>
      </ul>
      <ul class="nav navbar-nav navbar-right">
        <li><a href="#" class="connection-status" id="connection-status">Connection Status</a></li>
        <li class="dropdown">
          <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false"><span id="session-active">User</span> <span class="caret"></span></a>
          <ul class="dropdown-menu">
            <li><a href="#" id="user_name"></a></li>
            <li><a href="#" class="subject-id"></a></li>
            <li><a href="#" class="session-id"></a></li>
            <li role="separator" class="divider"></li>
            <li><a href="#" onclick="closeSession();">Close Session</a></li>
            <li><a href="#" onclick="logout();">Logout</a></li>
          </ul>
        </li>
      </ul>
    </div><!-- /.navbar-collapse -->
  </div><!-- /.container-fluid -->
</nav>

  <!-- start session button -->
  <section id="admin-top" class="bg-light-gray">
    <div class="container">
      <div class="row">
        <div class="col-md-12">
          <center>
            <button class="btn btn-primary btn-lg" data-toggle="modal" data-target="#defineSession" title="Start a new assessment session">New Session</button>
          </center>
        </div>
      </div>
    </div>
  </section>

  <!-- Non-modal calendar -->
  <section id="calendar-top" class="bg-light-gray">
    <div class="container">
      <div class="row">
        <div class="col-lg-12">
          &nbsp;
        </div>
      </div>
      <div class="row">
        <div id='calendar-loc'></div>
      </div>
      <div class="row">
        &nbsp;
      </div>
    </div>
  </section>

  <section class="bg-light-gray">
    <div class="container">
      <div class="row">
        <div class="col-lg-12">
          <center>
            <button class="btn btn-primary btn-lg" data-toggle="modal" data-target="#saveSession" id="open-save-session">Save Session</button>
          </center>
        </div>
      </div>
    </div>
  </section>

  <div class="portfolio-modal modal fade" id="saveSession" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-content">
      <div class="close-modal" data-dismiss="modal">
        <div class="lr">
          <button class="close">x</button>
        </div>
      </div>
      <div class="container">
        <div class="row">
          <div class="col-lg-12">
            <div class="modal-body">
              <h3>Finish and upload the current session?</h3>
              <form name="sentMessage" id="sessionInfoForm" novalidate>
                <div class="col-md-6">

                  <div class="form-group">
                    <label for="session-participant" class="control-label">Confirm Participant ID</label>
                    <input type="text" class="form-control" placeholder="NDAR-#####" id="session-participant-again" required data-validation-required-message="Please enter the participant NDAR ID.">
                    <p class="help-block text-danger"></p>
                  </div>

                  <button id="save-session-button" type="button" class="btn btn-success" data-dismiss="modal"><i class="fa fa-save"></i> Save Session</button> &nbsp;
                  <button type="button" class="btn btn-default" data-dismiss="modal"><i class="fa fa-times"></i> Back</button>&nbsp;
                </div>
              </form>
            </div><!-- /.modal-body -->
          </div><!-- /.col-lg-12 -->
        </div><!-- /.row -->
      </div><!-- /.container -->
    </div><!-- /.modal-content -->
  </div><!-- /.portfolio-modal -->
  
  <!-- define session -->
  <div class="portfolio-modal modal fade" id="defineSession" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-content">
      <div class="close-modal" data-dismiss="modal">
        <div class="lr">
          <button class="close">x</button>
        </div>
      </div>
      <div class="container">
        <div class="row">
          <div class="col-lg-12">
            <div class="modal-body">
              <h3>Assessment Setup</h3>
              <form name="sentMessage" id="sessionInfoForm" novalidate>
                <div class="col-md-6">

                  <div class="form-group">
                    <label for="session-participant" class="control-label">Participant</label>
                    <input type="text" class="form-control" placeholder="NDAR-#####" id="session-participant" required data-validation-required-message="Please enter the participant NDAR ID.">
                    <p class="help-block text-danger"></p>
                  </div>

                  <div class="form-group">
                    <label for="session-name" class="control-label">Session name</label>
                    <input type="text" class="form-control" placeholder="Baseline-01" id="session-name" required data-validation-required-message="Please enter the session ID.">
                    <p class="help-block text-danger"></p>
                  </div>

                  <div class="form-group">
                    <label for="session-months" class="control-label">Number of months captured</label>
                    <input type="text" class="form-control" placeholder="3" id="session-months" required data-validation-required-message="Please enter the number of months since the last assessment." value="3">
                    <p class="help-block text-danger"></p>
                  </div>

                  <div class="form-group">
                    <label for="session-date" class="control-label">Session Date</label>
                    <div class='input-group date' id='session-date-picker'>
                      <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="session-date" class="form-control" placeholder="(TODO: Fill in with the current date)" />
                      <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                      </span>
                    </div>
                  </div>

                  <div class="clearfix"></div>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-lg-12">
            <div class="modal-body">
              <form role="form" class="form-horizontal">
                <div class="col-md-12">

                  <!-- substances -->
                  <div class="form-group">
                    <label class="control-label" for="select-substances-checkboxes">Substances <span id="num-selected-substances">(none selected)</span></label>
                    <div class="btn-group btn-group-lg" style="margin-top: 5px;" data-toggle="buttons" id="select-substances-checkboxes"> </div>
                  </div>

                  <div class="form-group">
                    <label class="control-label" for="sessions-table">Special Events Range:</label>&nbsp;<span class="session-date-range"></span>
                    <table class="table" id="sessions-table">
                      <thead>
                        <tr>
                          <th>Event name</th>
                          <th>Start date</th>
                          <th>End date</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td><input type="text" class="form-control" id="special-event-01-name" placeholder="Event name"></td>
                          <td>
                            <div class='input-group date' id='special-event-01-start-date-picker'>
                              <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-01-start-date" class="form-control" />
                              <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                              </span>
                            </div>
                          </td>
                          <td>
                            <div class='input-group date' id='special-event-01-end-date-picker'>
                              <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-01-end-date" class="form-control" />
                              <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                              </span>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td><input type="text" class="form-control" id="special-event-02-name" placeholder="Event name"></td>
                          <td>
                            <div class='input-group date' id='special-event-02-start-date-picker'>
                              <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-02-start-date" class="form-control" />
                              <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                              </span>
                            </div>
                          </td>
                          <td>
                            <div class='input-group date' id='special-event-02-end-date-picker'>
                              <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-02-end-date" class="form-control" />
                              <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                              </span>
                            </div>
                          </td>
                        </tr>
                        <tr>
                          <td><input type="text" class="form-control" id="special-event-03-name" placeholder="Event name"></td>
                          <td>
                            <div class='input-group date' id='special-event-03-start-date-picker'>
                              <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-03-start-date" class="form-control" />
                              <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                              </span>
                            </div>
                          </td>
                          <td>
                            <div class='input-group date' id='special-event-03-end-date-picker'>
                              <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-03-end-date" class="form-control" />
                              <span class="input-group-addon">
                                <span class="glyphicon glyphicon-calendar"></span>
                              </span>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div><!-- /.form-group -->
                </div><!-- /.col-md-12 -->
              </form>
              <div>
                <button id="open-calendar-button" type="button" class="btn btn-success" data-dismiss="modal"><i class="fa fa-save"></i> Start Followback Timeline</button> &nbsp;
                <button type="button" class="btn btn-default" data-dismiss="modal"><i class="fa fa-times"></i> Back</button>&nbsp;
              </div>
            </div><!-- /.modal-body -->
          </div><!-- /.col-lg-12 -->
        </div><!-- /.row -->
      </div><!-- /.container -->
    </div><!-- /.modal-content -->
  </div><!-- /.portfolio-modal -->

  <!-- add event -->
  <div class="portfolio-modal modal fade" id="addEvent" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-content">
      <div class="close-modal" data-dismiss="modal">
        <div class="lr">
          <div class="rl">
          </div>
        </div>
      </div>
      <div class="container">
        <div class="row">
          <div class="col-lg-8 col-lg-offset-2">
            <div class="modal-body">
              <!-- Details Go Here -->
              <h2>Event Details</h2>
              <!-- <p class="item-intro text-muted" id="add-event-message">Edit the event.</p> -->
              <form role="form" class="form-horizontal">

                <!-- hidden field to remember the orginal event -->
                <input type="hidden" id="add-event-origevent"/>

                <!-- substance -->
                <div class="form-group has-feedback">
                  <label class="control-label col-sm-3" for="add-event-substance" title="Substance type">Substance</label>
                  <div class="col-sm-9">
                    <div class="input-group">

                      <div class="input-group-btn">
                        <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select <span class="caret"></span></button>
                        <ul class="dropdown-menu dropdown-menu-right multi-level" role="menu" id="substance-list"> </ul>
                      </div>
                      <input type="text" class="form-control" aria-label="..." id="add-event-substance">
                    </div>
                  </div>
                </div>

                <!-- amount -->
                <div class="form-group has-feedback">
                  <label class="control-label col-sm-3" for="add-event-amount">Amount</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <input type="text" class="form-control" aria-label="..." id="add-event-amount">
                      <div class="input-group-addon">grams</div>
                    </div>
                  </div>
                </div>

                <!-- title -->
                <div class="form-group has-feedback">
                  <label class="control-label col-sm-3" for="add-event-title">Title</label>
                  <div class="col-sm-9">
                    <input type="text" class="form-control" id="add-event-title" placeholder="amount units of substance">
                  </div>
                </div>

                <!-- start date picker -->
                <div class="form-group has-feedback">
                  <label class="control-label col-sm-3" for="add-event-start-time">Start Time</label>
                  <div class="col-sm-9">
                    <div class='input-group date' id='add-event-start-date-picker'>
                      <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="add-event-start-time" class="form-control" />
                      <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                      </span>
                    </div>
                  </div>
                </div>

                <!-- end date picker -->
                <div class="form-group has-feedback" id="display-end-time">
                  <label class="control-label col-sm-3" for="add-event-end-time">End Time</label>
                  <div class="col-sm-9">
                    <div class='input-group date' id='add-event-end-date-picker'>
                      <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="add-event-end-time" class="form-control" />
                      <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                      </span>
                    </div>
                  </div>
                </div>

                <!-- checkbox to enable selecting the days of the week -->
                <div class="form-group has-feedback">
                  <label class="control-label col-sm-3" for="add-event-recurring"></label>
                  <div class="col-sm-9">
                    <div class="checkbox">
                      <label for="add-event-recurring">
                        <input type="checkbox" id="add-event-recurring" value="">Event recurring
                      </label>
                    </div>
                  </div>
                </div>

                <!-- days of the week -->
                <div class="form-group" id="recurring-details" style="display: none;">
                  <label class="control-label col-sm-3" for="add-event-days-of-week">Days</label>
                  <div class="col-sm-9">
                  <div class="btn-group" data-toggle="buttons" id="add-event-days-of-week">
                    <label class="btn btn-default">
                      <input type="checkbox" name="options" id="sunday"> Sun
                    </label>
                    <label class="btn btn-default">
                      <input type="checkbox" name="options" id="monday"> Mon
                    </label>
                    <label class="btn btn-default">
                      <input type="checkbox" name="options" id="tuesday"> Tue
                    </label>
                    <label class="btn btn-default">
                      <input type="checkbox" name="options" id="wednesday"> Wed
                    </label>
                    <label class="btn btn-default">
                      <input type="checkbox" name="options" id="thursday"> Thu
                    </label>
                    <label class="btn btn-default">
                      <input type="checkbox" name="options" id="friday"> Fri
                    </label>
                    <label class="btn btn-default">
                      <input type="checkbox" name="options" id="saturday"> Sat
                    </label>
                  </div>
                  </div>
                </div>

                <!-- hidden checkbox for fullday event -->
                <div class="form-group has-feedback">
                  <div class="checkbox" style="display: none;">
                    <label for="add-event-fullday">
                      <input id="add-event-fullday" type="checkbox" value="">full day
                    </label>
                  </div>
                </div>

              </form>

              <button id="save-event-button" style="margin-top: 50px;" type="button" class="btn btn-success" data-dismiss="modal"><i class="fa fa-save"></i> Save</button>
              <button style="margin-top: 50px;" type="button" class="btn btn-primary" data-dismiss="modal"><i class="fa fa-times"></i> Close</button>
              <button id="delete-event-button" style="margin-top: 50px;" type="button" class="btn btn-warning pull-right" data-dismiss="modal"><i class="fa fa-close"></i> Delete Event</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
  <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script>
  <script src='js/moment.min.js'></script>

  <!-- allow users to download tables as csv and excel -->
  <script src="js/excellentexport.min.js"></script>

  <!-- Bootstrap Core JavaScript -->
  <script src="js/bootstrap.min.js"></script>

  <script src="js/bootstrap-datetimepicker.js"></script>
  <script src="js/bootstrap-datepicker.js"></script>
  <script src="js/bootstrap-colorselector.js"></script>

  <!-- Plugin JavaScript -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-easing/1.3/jquery.easing.min.js"></script>

  <!-- Contact Form JavaScript -->
  <script src="js/jqBootstrapValidation.js"></script>
  <script src="js/contact_me.js"></script>

  <!-- Custom Theme JavaScript -->
  <script src="js/agency.js"></script>
  <script src='js/fullcalendar.min.js'></script>

  <script src="js/d3.v3.min.js"></script>

  <script type="text/javascript" src="js/all.js"></script>

</body>

</html>
