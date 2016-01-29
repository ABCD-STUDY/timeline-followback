<?php
  session_start();

  include($_SERVER["DOCUMENT_ROOT"]."/code/php/AC.php");
  $user_name = check_logged(); /// function checks if visitor is logged.
  //$user_name = "admin";
  $admin = false;

  if ($user_name == "") {
    // user is not logged in

  } else {
    $admin = true;
    echo('<script type="text/javascript"> user_name = "'.$user_name.'"; </script>'."\n");
    echo('<script type="text/javascript"> admin = '.($admin?"true":"false").'; </script>'."\n");
  }
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
  <!--link href="css/agency.css" rel="stylesheet"--> <!-- yellow and black theme -->
  <!-- required for the date and time pickers -->
  <link href="css/bootstrap-datetimepicker.css" rel="stylesheet" type="text/css">

  <link rel='stylesheet' href='//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.6.0/fullcalendar.min.css' />
  <!-- media="print" is required to display the fullcalendar header buttons -->
  <link rel='stylesheet' media='print' href='//cdnjs.cloudflare.com/ajax/libs/fullcalendar/2.6.0/fullcalendar.print.css' />

  <link rel="stylesheet" href="css/style.css">

</head>

<body>

  <!-- User Administration section -->
  <!-- TODO: Change this to a navigation bar -->
  <section id="admin-top" class="bg-light-gray">
    <div class="container">
      <div class="row" style="margin-top: 10px;">
        <div class="col-md-12">

          <div class="btn pull-right connection-status" id="connection-status">Connection Status</div>

          <div>
            <a href="#" class="btn btn-default" onclick="logout();">Logout</a>&nbsp;
            <label>user name: </label>&nbsp;<label id="user_name"></label>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="col-md-12">
	  <center>
            <button class="btn btn-primary btn-lg" data-toggle="modal" data-target="#defineSession">Define New Session</button>
	  </center>
	</div>
      </div>	
    </div>
  </section>

  <!-- Session information section -->
<!--   <section id="contact">
    <div class="container">
      <div class="row">
        <div class="col-lg-12">
          <h2 class="section-heading">Session information</h2>
        </div>
      </div>
      <div class="row">
        <div class="col-lg-12">
          <form name="sentMessage" id="sessionInfoForm" novalidate>
            <div class="row">
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
                  <input type="number" class="form-control" placeholder="3" id="session-months" required data-validation-required-message="Please enter the number of months since the last assessment." value="3">
                  <p class="help-block text-danger"></p>
                </div>

                <div class="form-group">
                  <label for="session-date" class="control-label">Session Date</label>
                    <div class='input-group date' id='session-date-picker'>
                      <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="session-date" class="form-control" />
                      <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                      </span>
                    </div>
                </div>

              </div>
                <div class="clearfix"></div>
                <div class="col-lg-12">
                  <a href="#" class="btn btn-primary" onclick="openSubstancesForm();">Start Session</a>
              </div>

            </div>
          </form>
        </div>
      </div>
    </div>
  </section> -->

  <!-- List of sessions -->
  <!-- HIDE THIS FOR NOW 
  <div>
    <table class="table-striped table table-condensed" id="sessions-table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Participant ID</th>
          <th>Session ID</th>
          <th>User</th>
          <th>Site ID</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody id="sessions-list"></tbody>
    </table>
  </div>
  -->

  <!-- Button trigger modal -->
  <!-- <button type="button" class="btn btn-primary btn-lg" data-toggle="modal" data-target="#modal-calendar">
    Open Modal Calendar
  </button> -->

  <!-- -->
<!--   <div class="portfolio-modal modal fade" id="modal-calendar" tabindex="-1" role="dialog" aria-hidden="true">
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

          <div class="container">
            <div style="height: 100%; width: 100%; position: relative;">
               <div id='calendar-loc'></div>
            </div>
          </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  </div> -->
  <!-- -->

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
  <!-- -->
  
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
              <h3>Define a new session</h3>
    
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
                    <label class="control-label" for="select-substances-checkboxes">Substances <span id="num-selected-substances"></span></label>
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
                  </div>
		</div>  
	      </form>
	      
	      <!-- <button style="margin-top: 50px;" type="button" class="btn btn-primary" data-dismiss="modal"><i class="fa fa-times"></i> Back</button> -->
	      
	      
	      
              <div>
                <button id="open-calendar-button" type="button" class="btn btn-success" data-dismiss="modal"><i class="fa fa-save"></i> Start Followback Timeline</button> &nbsp;
                <button type="button" class="btn btn-default" data-dismiss="modal"><i class="fa fa-times"></i> Back</button>&nbsp;
                <!-- <a href="#" class="btn btn-primary" onclick="openSubstancesForm();">Start Session</a> -->
	      </div>
	      
	      
	      <!--         <button id="save-session-button" style="margin-top: 50px;" type="button" class="btn btn-success" data-dismiss="modal"><i class="fa fa-save"></i> </button>
			   <button style="margin-top: 50px;" type="button" class="btn btn-primary" data-dismiss="modal"><i class="fa fa-times"></i> Back</button>
			   <button id="delete-session-button" style="margin-top: 50px;" type="button" class="btn btn-warning pull-right" data-dismiss="modal"><i class="fa fa-close"></i> Delete Session</button> -->
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  



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
  <!--script src="//cdnjs.cloudflare.com/ajax/libs/moment.js/2.11.1/moment.min.js"></script-->
  <script src='js/moment.min.js'></script>

  <!-- allow users to download tables as csv and excel -->
  <script src="js/excellentexport.min.js"></script>

  <!-- Bootstrap Core JavaScript -->
  <script src="js/bootstrap.min.js"></script>

  <script src="js/bootstrap-datetimepicker.js"></script>
  <script src="js/bootstrap-datepicker.js"></script>
  <script src="js/bootstrap-colorselector.js"></script>

  <!-- Plugin JavaScript -->
  <!-- MISSING FILES
  <script src="//cdnjs.cloudflare.com/ajax/libs/jquery-easing/1.3/jquery.easing.min.js"></script>
  -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery-easing/1.3/jquery.easing.min.js"></script>
  <!--script src="js/classie.js"></script--> <!-- required by cbpAnimatedHeader.js -->
  <!--script src="js/cbpAnimatedHeader.js"></script--> <!-- required for animated navigation bar -->

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
