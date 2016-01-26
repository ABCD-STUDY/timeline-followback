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

</head>

<body>

  <!-- Session information section -->
  <section id="contact">
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
                  <input type="text" class="form-control" placeholder="Participant number *" id="participantNumber" required data-validation-required-message="Please enter the participant number.">
                  <p class="help-block text-danger"></p>
                </div>

                <div class="form-group">
                  <input type="text" class="form-control" placeholder="Session number *" id="sessionNumber" required data-validation-required-message="Please enter the session number.">
                  <p class="help-block text-danger"></p>
                </div>

                <div class="form-group">
                  <input type="text" class="form-control" placeholder="Follow-up period *" id="followUpPeriod" required data-validation-required-message="Please the follow-up period.">
                  <p class="help-block text-danger"></p>
                </div>

                <!-- start date picker -->
                <div class="form-group has-feedback">
                  <label class="control-label col-sm-3" for="session-date">Date *</label>
                  <div class="col-sm-9">
                    <div class='input-group date' id='datetimepicker1'>
                      <input type='text' data-format="MM/dd/yyyy HH:mm:ss PP" id="session-date" class="form-control" />
                      <span class="input-group-addon">
                        <span class="glyphicon glyphicon-calendar"></span>
                      </span>
                    </div>
                  </div>
                </div>

              </div>
              <div class="clearfix"></div>
              <div class="col-lg-12">
                <div id="success"></div>
                <button type="submit" class="btn btn-primary">Save</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </section>

  <!-- List of sessions -->
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

  <!-- Calendar section -->
  <section id="calendar-top" class="bg-light-gray">
    <div class="container">
      <div class="row">
        <div class="col-lg-12">
          <h2 class="section-heading">Calendar</h2>
        </div>
      </div>
      <div id='calendar-loc'></div>
    </div>
  </section>

  <!-- User Administration section -->
  <section id="admin-top" class="bg-light-gray">
    <div class="container">

      <div class="row">
        <div class="col-lg-12">
          <h2 class="section-heading">User Administration</h2>
        </div>
      </div>
      <div>
        <a href="#" class="btn btn-primary" onclick="logout();">Logout</a>
        <label>Logged in as: </label><label id="user_name"></label>
        <label>Roles: </label><label id="roles"></label>
      </div>

    </div>
  </section>

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
              <p class="item-intro text-muted" id="add-event-message">Edit the event.</p>
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
                        <ul class="dropdown-menu dropdown-menu-right multi-level" role="menu" id="substance-list">
                          <li><a class="substance-selection" href="#">alcohol</a></li>
                          <li><a class="substance-selection" href="#">tobacco</a></li>
                          <li><a class="substance-selection" href="#">marijuana</a></li>
                        </ul>
                      </div>
                      <input type="text" class="form-control" aria-label="..." id="add-event-substance">
                    </div>
                  </div>
                </div>

                <!-- substance -->
                <div class="form-group">
                  <label class="control-label col-sm-3" for="add-event-substance2">Days</label>
                  <div class="col-sm-9">
                  <div class="btn-group" data-toggle="buttons" id="add-event-substance2">
                    <label class="btn btn-default">
                      <input type="radio" name="options" id="alcohol"> Alcohol
                    </label>
                    <label class="btn btn-default">
                      <input type="radio" name="options" id="tobacco"> Tobacco
                    </label>
                    <label class="btn btn-default">
                      <input type="radio" name="options" id="marijuana"> Marijuana
                    </label>
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

                <!-- units -->
                <div class="form-group has-feedback">
                  <label class="control-label col-sm-3" for="add-event-units" title="Units of measuremnt">Units</label>
                  <div class="col-sm-9">
                    <div class="input-group">
                      <div class="input-group-btn">
                        <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select <span class="caret"></span></button>
                        <ul class="dropdown-menu dropdown-menu-right multi-level" role="menu" id="units-list">
                          <li><a class="units-selection" href="#">gr</a></li>
                          <li><a class="units-selection" href="#">ml</a></li>
                          <li><a class="units-selection" href="#">oz</a></li>
                        </ul>
                      </div>
                      <input type="text" class="form-control" aria-label="..." id="add-event-units">
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
                    <div class='input-group date' id='datetimepicker1'>
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
                    <div class='input-group date' id='datetimepicker2'>
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
                <div class="form-group">
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

  <script type="text/javascript">

// logout the current user
function logout() {
  jQuery.get('/code/php/logout.php', function(data) {
    if (data == "success") {
      // user is logged out, reload this page
    } else {
      alert('something went terribly wrong during logout: ' + data);
    }
    window.location.href = "/applications/User/login.php";
  });
}

function reloadContacts() {
  // remove all rows from the table
  jQuery('#contacts-list').children().remove();

  // fill the table with the list of contacts
  jQuery.getJSON('getSessions.php?action=load', function( refs ) {
    console.log( refs.length );
    refs.sort(function(a,b) { return b.date - a.date; });
    for (var i = 0; i < refs.length; i++) {
      var d = new Date(refs[i].date*1000);
      jQuery('#sessions-list').append('<tr contact-id="' + refs[i].id + '" title="last changed: ' + d.toDateString() + '"><td>'+ refs[i].date + '</td><td>'+ refs[i].id + '</td><td>'+ refs[i].sessionID + '</td><td>' + refs[i].userName + '</td><td>' + refs[i].siteID + '</td><td>' + refs[i].status + '</td></tr>');
    }
    jQuery('#sessions-table').DataTable();
  });
}

  var recurring;
  jQuery('#add-event-recurring').change(function() {
    recurring = this.checked;
    jQuery('#add-event-days-of-week').prop('disabled', !recurring);
    if (recurring) {
      jQuery('#add-event-days-of-week').css('visibility', 'visible');
    } else {
      jQuery('#add-event-days-of-week').css('visibility', 'hidden');
    }
  });

  var sunday;
  jQuery('#sunday').change(function() {
    sunday = this.checked;
    // OR: var sunday = jQuery('#sunday').prop('checked');
  });

  var monday;
  jQuery('#monday').change(function() {
    monday = this.checked;
  });

  var tuesday;
  jQuery('#tuesday').change(function() {
    tuesday = this.checked;
  });

  function specifyEvent( event ) {
    if (!eventEditable(event).ok) {
      jQuery('#add-event-message').html("This event cannot be edited because " + eventEditable(event).message + ".");
      jQuery('#add-event-title').prop('disabled', true);
      jQuery('#save-event-button').prop('disabled', true);
      jQuery('#delete-event-button').prop('disabled', true);
      jQuery('#datetimepicker1').prop('disabled', true);
      jQuery('#datetimepicker2').prop('disabled', true);
      jQuery('#add-event-substance').prop('disabled', true);
      jQuery('#add-event-amount').prop('disabled', true);
      jQuery('#add-event-units').prop('disabled', true);
      jQuery('#add-event-start-time').prop('disabled', true);
      jQuery('#add-event-end-time').prop('disabled', true);
    } else {
      jQuery('#add-event-message').html("Edit the event.");
      jQuery('#add-event-title').prop('disabled', true);
      jQuery('#save-event-button').prop('disabled', false);
      jQuery('#delete-event-button').prop('disabled', false);
      jQuery('#datetimepicker1').prop('disabled', false);
      jQuery('#datetimepicker2').prop('disabled', false);
      jQuery('#add-event-substance').prop('disabled', true);
      jQuery('#add-event-amount').prop('disabled', false);
      jQuery('#add-event-units').prop('disabled', true);
      jQuery('#add-event-start-time').prop('disabled', false);
      jQuery('#add-event-end-time').prop('disabled', false);
    }

    jQuery('#addEvent').modal( 'show');
    setTimeout(function() {
      jQuery('#add-event-title').focus();
    }, 200);
    
    // store the event in the name dom element (we have to move it later if it exists already)
    jQuery('#add-event-origevent').data('origevent', event);

    jQuery('#delete-event-button').data('eid', event.eid);

    jQuery('#add-event-title').val(event.title);
    jQuery('#add-event-substance').val(event.substance);
    jQuery('#add-event-amount').val(event.amount);
    jQuery('#add-event-units').val(event.units);
    
    var cal = $('#calendar-loc').fullCalendar('getCalendar');
    var s = cal.moment(event.start).format();
    var e = cal.moment(event.end).format();

    if (event.fullDay) {
      jQuery('#add-event-fullday').prop('checked', true);
      jQuery('#display-end-time').show();
    } else {
      jQuery('#add-event-fullday').prop('checked', false); 
      jQuery('#display-end-time').show();
    }

    jQuery('#save-event-button').attr('event-start', s);
    jQuery('#save-event-button').attr('event-end', e);

    // initialize the field for the start date
    //jQuery('#datetimepicker1').data("DateTimePicker").setMinDate(new Date());
    jQuery('#datetimepicker1').data("DateTimePicker").setDate(event.start);

    // initialize the field for the end date
    //jQuery('#datetimepicker2').data("DateTimePicker").setMinDate(new Date());
    jQuery('#datetimepicker2').data("DateTimePicker").setDate(event.end);

  }

  // load the events
  function loadEvents() {
    console.log("function loadEvents()");

    jQuery.getJSON('code/php/events.php?action=list', function(data) {
      console.log('response: '+ data)

      for (var i = 0; i < data.length; i++) {
        var event = new Object();

        event.substance = data[i].substance;
        event.amount = data[i].amount;
        event.units = data[i].units;

        event.title =  event.substance + ' (' + event.amount + ' ' + event.units + ')';
        event.start = moment.parseZone(data[i].start);
        event.end   = moment.parseZone(data[i].end);
        event.user    = data[i].user;
        event.eid     = data[i].eid; // event id

        if (eventEditable(event).ok) {
          console.log(eventEditable(event).ok);
          // enable drag and drop for events
          event.editable = true;
        } else {
          event.editable = false;
        }

        jQuery('#calendar-loc').fullCalendar('renderEvent', event, true);
      }
    });        
  }

  moment.fn.roundNext15Min = function () {
    var intervals = Math.floor((this.minutes()+(15/2.0)) / 15);
    if(intervals == 4) {
      this.add('hours', 1);
      intervals = 0;
    }
    this.minutes(intervals * 15);
    this.seconds(0);
    return this;
  }

  // save a new calendar event
  function storeEvent( event ) {
    console.log("function storeEvent( event )");

    // check if the event is not editable
    if (!eventEditable(event).ok) {
      alert("Error: This event could not be stored. Maybe you don't have permissions, or its in the quarantine zone (past or immediate future).");
      return false; // do nothing
    }

    var cal = jQuery('#calendar-loc').fullCalendar('getCalendar');
    var s = cal.moment(event.start).format();
    var e = cal.moment(event.end).format();
    // round events at 15 minutes
    s = event.start.roundNext15Min().format();
    e = event.end.roundNext15Min().format();

    // form a url to create the event
    var url = encodeURI('code/php/events.php' +
      '?action=create' +
      '&value=' + event.title +
      '&value2=' + encodeURIComponent(s) +
      '&value3=' + encodeURIComponent(e) +
      '&value5=' + 'event.noshow' +
      '&value6=' + 'event.referrer' +
      '&value7=' + event.substance +
      '&value8=' + event.amount +
      '&value9=' + event.units);

    // send the url to create the event
    jQuery.getJSON(url, function(data) {
      console.log('response: '+ data.message)

      // if the response is ok
      if (data.ok == 1) {
        // check if an event id was defined
        if (typeof(data.eid) !== 'undefined') {
          // set the event id
          event.eid = data.eid;
          console.log(event)
          // render the event to the calendar
          jQuery('#calendar-loc').fullCalendar('renderEvent', event, true);
        } else {
          alert("Error: data.eid is not defined");
        }
      } else {
        alert(data.message);
      }
    });
    return true;
  }

  // remove an event
  function removeEvent( event ) {
    console.log("function removeEvent( event )");

    // check if the event is not editable
    if (!eventEditable(event).ok) {
      alert("Error: This event could not be removed. The event is not editable.");
      return; // do nothing
    }

    // form a url to remove the event
    var url = encodeURI('code/php/events.php' +
      '?action=remove' +
      '&value=' + event.title +
      '&value2=' + encodeURIComponent(event.start.format()) +
      '&value3=' + encodeURIComponent(event.end.format()) +
      '&value4=' + encodeURIComponent(event.eid));

    // send the url to remove the event
    jQuery.getJSON(url, function(data) {
      console.log('response: '+ data.message)

      // if the response is ok
      if (data.ok == 1) {
        // now delete the event from the calendar as well
        var events = jQuery('#calendar-loc').fullCalendar('clientEvents');
        events.forEach(function(e) {
          if (typeof(event.eid) !== 'undefined' && e.eid == event.eid) {
            console.log("jQuery('#calendar-loc').fullCalendar('removeEvents', e._id)");
            jQuery('#calendar-loc').fullCalendar('removeEvents', e._id);
          }
        });
      } else {
        alert(data.message);
      }
    });
  }

  // update an event
  function updateEvent( event ) {
    console.log("function updateEvent( event )");

    // check if the event is not editable
    if (!eventEditable(event).ok) {
      alert("Error: This event cannot be changed. Maybe you don't have permissions, it is in the past or the immediate future (+72hours).");
      return false; // do nothing
    }
    //var cal = jQuery('#calendar-loc').fullCalendar('getCalendar');
    //var s = cal.moment(event.start).format();
    //var e = cal.moment(event.end).format();
    var s = event.start.format();
    var e = event.end.format();

    // WHY? If we drag-and-drop we don't get the time zone here
    // We add the correct time zone to the string for Los Angeles
    if (event.start.zone() == 0) {
      s = s + "-08:00";
    }
    if (event.end.zone() == 0) {
      e = e + "-08:00";
    }

    // form a url to update the event
    var url = encodeURI('code/php/events.php' +
      '?action=update' +
      '&value=' + event.title +
      '&value2=' + encodeURIComponent(s) +
      '&value3=' + encodeURIComponent(e) +
      '&value4=' + encodeURIComponent(event.eid) +
      '&value5=' + 'event.noshow' +
      '&value6=' + 'event.referrer' +
      '&value7=' + event.substance +
      '&value8=' + event.amount +
      '&value9=' + event.units);

    // send the url to update the event
    jQuery.getJSON(url, function(data) {
      console.log('response: '+ data.message)

      // if the response is ok
      if (data.ok == 1) {
        // update the calendar event
        jQuery('#calendar-loc').fullCalendar('updateEvent', event);
      } else {
        alert(data.message);
      }
    });
    return true;
  }

  // check if an event is editable
  function eventEditable( event ) {
    return {ok: true}; // allow all changes
  }

  // triggered when the user presses the save button
  jQuery('#save-event-button').click(function() {

    var ev = new Object();

    // if we change an existing event this should exist
    var originalEvent = jQuery('#add-event-origevent').data('origevent');
    if (typeof(originalEvent) !== 'undefined') {
      // start from here (copies event id in eid)
      ev = originalEvent;
    }
    //ev.eid   = jQuery('#delete-event-button').data('eid');

    ev.user = user_name;
    ev.fullDay = jQuery('#add-event-fullday').prop('checked');
    ev.substance = jQuery('#add-event-substance').val();
    ev.amount   = jQuery('#add-event-amount').val();
    ev.units = jQuery('#add-event-units').val();
    ev.title =  ev.substance + ' (' + ev.amount + ' ' + ev.units + ')';
    ev.editable = true;

    ////////////////////////////////////
    //
    // This seems to be broken, I get two different dates from picker1 and picker2,
    // in order to fix, replace time zone if its in UTC (== "+00:00")
    //
    ////////////////////////////////////
    var offsetInMinutes = moment().zone();
    ev.start = jQuery('#datetimepicker1').data('DateTimePicker').getDate().format();
    ev.end   = jQuery('#datetimepicker2').data('DateTimePicker').getDate().format();
    ev.start = ev.start.replace("+00:00", "-08:00");
    ev.end   = ev.end.replace("+00:00", "-08:00");
    var cal  = jQuery('#calendar-loc').fullCalendar('getCalendar');
    ev.start = cal.moment(ev.start);
    ev.end   = cal.moment(ev.end);

    if (typeof(ev.eid) !== 'undefined') {
      if (!updateEvent(ev)) {
        jQuery('#calendar-loc').fullCalendar('refetchEvents');
      }
      } else {
        if (!storeEvent(ev)) {
        jQuery('#calendar-loc').fullCalendar('refetchEvents');
      }
    }
  });

  // required to display the date and time picker
  jQuery('#datetimepicker1').datetimepicker({language: 'en' });
  jQuery('#datetimepicker2').datetimepicker({language: 'en' });

  jQuery("#datetimepicker1").on("change.dp",function (e) {
     //jQuery('#datetimepicker2').data("DateTimePicker").setMinDate(e.date);
  });
  jQuery("#datetimepicker2").on("change.dp",function (e) {
     //jQuery('#datetimepicker1').data("DateTimePicker").setMaxDate(e.date);
  });

  // triggered with the user selects the substance dropdown menu
  jQuery(document).on('click', '.substance-selection', function(event) {
    event.preventDefault();
    jQuery('#add-event-substance').val( jQuery(this).text() );
  });

  // triggered with the user selects the units dropdown menu
  jQuery(document).on('click', '.units-selection', function(event) {
    event.preventDefault();
    jQuery('#add-event-units').val( jQuery(this).text() );
  });

  // triggered when the user presses the delete button
  jQuery('#delete-event-button').click(function() {
    console.log("jQuery('#delete-event-button').click(function()");

    var ev = new Object();
    ev.title = jQuery('#add-event-title').val();
    ev.start = jQuery('#datetimepicker1').data('DateTimePicker').getDate();
    ev.end   = jQuery('#datetimepicker2').data('DateTimePicker').getDate();
    ev.eid   = jQuery('#delete-event-button').data('eid');
    removeEvent(ev);
  });

  // setup the calendar
  jQuery('#calendar-loc').fullCalendar({
    
    // defines the buttons and title at the top of the calendar
    header: { 
      left: 'prev,next today',
      center: 'title',
      right: ''
    },

    // the initial view when the calendar loads
    defaultView: 'month',

    // the starting time that will be displayed
    //minTime: '06:00:00',

    // the timezone in which dates throughout the API are parsed and rendered
    timezone: 'America/Los_Angeles',

    // allows a user to highlight multiple days or timeslots by clicking and dragging
    selectable: true,

    // draw a "placeholder" event while the user is dragging
    selectHelper: true,

    // triggered when the user clicks an event
    eventClick: function(calEvent, jsEvent, view) {
      console.log("eventClick: function(calEvent, jsEvent, view)");
      specifyEvent(calEvent);
    },

    // triggered when dragging stops and the event has moved to a different day/time
    eventDrop: function(calEvent, jsEvent, view) {
      console.log("eventDrop: function(calEvent, jsEvent, view)");
      if (!updateEvent(calEvent)) {
         jQuery('#calendar-loc').fullCalendar('refetchEvents');                 
      }
    },

    // triggered when resizing stops and the event has changed in duration
    eventResize: function(calEvent, jsEvent, view) {
      alert("eventResize: function(calEvent, jsEvent, view)");
     if (!updateEvent(calEvent)) {
        jQuery('#calendar-loc').fullCalendar('refetchEvents');                 
     }
    },

    // a method for programmatically selecting a period of time
    select: function(start, end) {
      var s = start.format();
      var e = end.format();
      console.log("select: function("+ s +", "+ e +")");

      // is this a full day event?
      var fullDay = !start.hasTime() && !end.hasTime();
      console.log("fullday: " + fullDay);

      // create a new event
      var eventData = {
        title: '',
        start: start,
        end: end,
        fullDay: fullDay
      };
      jQuery('#calendar-loc').fullCalendar('unselect');
      jQuery('#add-event-title').val("");
      jQuery('#add-event-substance').val("");
      jQuery('#add-event-amount').val("");
      jQuery('#add-event-units').val("");
      specifyEvent( eventData );
    }
  
  });

  jQuery(document).ready(function() {

  if (typeof user_name != 'undefined') {
    jQuery('#user_name').text(user_name);
    if (user_name == "admin") {
      console.log(user_name + "YES");
    } else {
      console.log(user_name + "NO");
    }
  }

  // if the user is an admin, then show the user admin button
  if (admin) {
    jQuery('#user_admin_button').prop('disabled', false);
  } else {
    jQuery('#user_admin_button').prop('disabled', true);
  }

    reloadContacts();
    loadEvents();
  });

  </script>

</body>

</html>
