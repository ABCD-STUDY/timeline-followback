  //----------------------------------------
  // User accounts
  //----------------------------------------
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

  function specifyEvent( event ) {
    if (!eventEditable(event).ok) {
      jQuery('#add-event-message').html("This event cannot be edited because " + eventEditable(event).message + ".");
      jQuery('#add-event-title').prop('disabled', true);
      jQuery('#save-event-button').prop('disabled', true);
      jQuery('#delete-event-button').prop('disabled', true);
      jQuery('#add-event-start-date-picker').prop('disabled', true);
      jQuery('#add-event-end-date-picker').prop('disabled', true);
      jQuery('#add-event-substance').prop('disabled', true);
      jQuery('#add-event-amount').prop('disabled', true);
      jQuery('#add-event-start-time').prop('disabled', true);
      jQuery('#add-event-end-time').prop('disabled', true);
    } else {
      jQuery('#add-event-message').html("Edit the event.");
      jQuery('#add-event-title').prop('disabled', true);
      jQuery('#save-event-button').prop('disabled', false);
      jQuery('#delete-event-button').prop('disabled', false);
      jQuery('#add-event-start-date-picker').prop('disabled', false);
      jQuery('#add-event-end-date-picker').prop('disabled', false);
      jQuery('#add-event-substance').prop('disabled', true);
      jQuery('#add-event-amount').prop('disabled', false);
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

    jQuery('#session-date-picker').data("DateTimePicker").setDate(event.start);

    jQuery('#special-event-01-start-date-picker').data("DateTimePicker").setDate(event.start);
    jQuery('#special-event-01-end-date-picker').data("DateTimePicker").setDate(event.start);
    jQuery('#special-event-02-start-date-picker').data("DateTimePicker").setDate(event.start);
    jQuery('#special-event-02-end-date-picker').data("DateTimePicker").setDate(event.start);
    jQuery('#special-event-03-start-date-picker').data("DateTimePicker").setDate(event.start);
    jQuery('#special-event-03-end-date-picker').data("DateTimePicker").setDate(event.start);

    // initialize the field for the start date
    //jQuery('#add-event-start-date-picker').data("DateTimePicker").setMinDate(new Date());
    jQuery('#add-event-start-date-picker').data("DateTimePicker").setDate(event.start);

    // initialize the field for the end date
    //jQuery('#add-event-end-date-picker').data("DateTimePicker").setMinDate(new Date());
    jQuery('#add-event-end-date-picker').data("DateTimePicker").setDate(event.end);

  }

  // load the events
  function loadEvents() {

    jQuery.getJSON('code/php/events.php?action=list', function(data) {

      for (var i = 0; i < data.length; i++) {
        var event = new Object();

        event.substance = data[i].substance;
        event.amount = data[i].amount;
        event.units = "";
        for (var j = 0; j < substance_units.length; j++) {
          if (substance_units[j][0] == event.substance) {
            event.units = substance_units[j][1];
            break;
          }
        }

        event.title =  event.substance + ' (' + event.amount + ' ' + event.units + ')';
        event.start = moment.parseZone(data[i].start);
        event.end   = moment.parseZone(data[i].end);
        event.user    = data[i].user;
        event.eid     = data[i].eid; // event id

        if (eventEditable(event).ok) {
          // enable drag and drop for events
          event.editable = true;
        } else {
          event.editable = false;
        }

        jQuery('#calendar-loc').fullCalendar('renderEvent', event, true);
      }
      // ugly workaround
      setTimeout(function() {
        jQuery("#calendar-loc").fullCalendar('render');
      }, 1000);

    });
  }

  // save a new calendar event
  function storeEvent( event ) {

    // check if the event is not editable
    if (!eventEditable(event).ok) {
      alert("Error: This event could not be stored. Maybe you don't have permissions, or its in the quarantine zone (past or immediate future).");
      return false; // do nothing
    }

    var cal = jQuery('#calendar-loc').fullCalendar('getCalendar');
    var s = cal.moment(event.start).format();
    var e = cal.moment(event.end).format();
    s = event.start.format();
    e = event.end.format();

    // form a url to create the event
    var url = encodeURI('code/php/events.php' +
      '?action=create' +
      '&value=' + event.title +
      '&value2=' + encodeURIComponent(s) +
      '&value3=' + encodeURIComponent(e) +
      '&value5=' + 'event.noshow' +
      '&value6=' + 'event.referrer' +
      '&value7=' + event.substance +
      '&value8=' + event.amount);

    // send the url to create the event
    jQuery.getJSON(url, function(data) {

      // if the response is ok
      if (data.ok == 1) {
        // check if an event id was defined
        if (typeof(data.eid) !== 'undefined') {
          // set the event id
          event.eid = data.eid;
          // render the event to the calendar
          jQuery('#calendar-loc').fullCalendar('renderEvent', event, true);
        } else {
          alert("Error: data.eid is not defined");
        }
      } else {
        // getting this error message:
        // Error: no site assigned to this user
        alert(data.message);
      }
    });
    return true;
  }

  // remove an event
  function removeEvent( event ) {

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

      // if the response is ok
      if (data.ok == 1) {
        // now delete the event from the calendar as well
        var events = jQuery('#calendar-loc').fullCalendar('clientEvents');
        events.forEach(function(e) {
          if (typeof(event.eid) !== 'undefined' && e.eid == event.eid) {
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

  // triggered when the user presses the start button
  jQuery('#open-calendar-button').click(function() {

    storeSubjectAndName();
    // update the calendar and display all special events
    createCalendar();
  });

  // triggered when the user presses the save button
  jQuery('#save-event-button').click(function() {

    var ev = new Object();

    // if we change an existing event this should exist
    var originalEvent = jQuery('#add-event-origevent').data('origevent');
    if (typeof(originalEvent) !== 'undefined') {

      // BUG: this if statement always evaluates as true,
      // even if no event was selected.

      // start from here (copies event id in eid)
      ev = originalEvent;
    }
    //ev.eid   = jQuery('#delete-event-button').data('eid');

    ev.user = user_name;
    ev.fullDay = jQuery('#add-event-fullday').prop('checked');
    ev.substance = jQuery('#add-event-substance').val();
    ev.amount    = jQuery('#add-event-amount').val();
    ev.title     =  ev.substance + ' (' + ev.amount + ' ' + ev.units + ')';
    ev.editable  = true;

    ////////////////////////////////////
    //
    // This seems to be broken, I get two different dates from picker1 and picker2,
    // in order to fix, replace time zone if its in UTC (== "+00:00")
    //
    ////////////////////////////////////
    var offsetInMinutes = moment().zone();
    ev.start = jQuery('#add-event-start-date-picker').data('DateTimePicker').getDate().format();
    ev.end   = jQuery('#add-event-end-date-picker').data('DateTimePicker').getDate().format();
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
  jQuery('#session-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#special-event-01-start-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#special-event-01-end-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#special-event-02-start-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#special-event-02-end-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#special-event-03-start-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#special-event-03-end-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#add-event-start-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#add-event-end-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });


  // triggered when the user selects the substance dropdown menu
  jQuery(document).on('click', '.substance-selection', function(event) {
    event.preventDefault();
    jQuery('#add-event-substance').val( jQuery(this).text() );
  });

  // triggered when the user selects the units dropdown menu
  jQuery(document).on('click', '.units-selection', function(event) {
    event.preventDefault();
    jQuery('#add-event-units').val( jQuery(this).text() );
  });

  // triggered when the user presses the delete button
  jQuery('#delete-event-button').click(function() {

    var ev = new Object();
    ev.title = jQuery('#add-event-title').val();
    ev.start = jQuery('#add-event-start-date-picker').data('DateTimePicker').getDate();
    ev.end   = jQuery('#add-event-end-date-picker').data('DateTimePicker').getDate();
    ev.eid   = jQuery('#delete-event-button').data('eid');
    removeEvent(ev);
  });

var calendar = null;
 
// setup the calendar
function createCalendar() {

    // copy the active substances to #substance-list
    var active_input_fields = jQuery('#select-substances-checkboxes input:checked');
    var active_substances = active_input_fields.map(function(a) { return [[ jQuery(active_input_fields[a]).attr('substance'), jQuery(active_input_fields[a]).attr('units') ]]; });
    for(var i = 0; i < active_substances.length; i++) {
	// jQuery('#substance-list').append("<li><a class=\"substance-selection\">" + active_substances[i] + "</a></li>");
	jQuery('#select-substance').append("<label class=\"btn btn-default substance-checkbox\"> <input type=\"checkbox\" name=\"options\" aria-invalid=\"false\" substance=\"" + active_substances[i][0] + "\" unit=\"" + active_substances[i][1] + "\">" + active_substances[i][0] + "</label>");
    }

    // if the calendar does not exist, create it (store in global variable)
    if (calendar == null) {
      calendar = jQuery('#calendar-loc').fullCalendar({
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
          specifyEvent(calEvent);
        },
	    
        // triggered when dragging stops and the event has moved to a different day/time
        eventDrop: function(calEvent, jsEvent, view) {
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
	    
            // is this a full day event?
            var fullDay = !start.hasTime() && !end.hasTime();
	    
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
            jQuery('#add-event-recurring').prop('checked', false);
            specifyEvent( eventData );
	},
        eventSources: [ "code/php/events.php", [
	      {
		  title: 'Some Holiday',
		  start: '2014-10-27'
	      }
	    ]]
	      
    });
  }

  // collect the current list of special events and add to the calendar (if they don't exist already)
  for (var i = 1; i < 4; i++) {

    var name = jQuery('#special-event-' + pad(i, 2) + '-name').val();
    if (name == "") {
      continue;
    }
    var d1 = jQuery('#special-event-' + pad(i, 2) + '-start-date').datetimepicker('getDate').val();
    var d2 = "";
    if (jQuery('#special-event-' + pad(i,2) + '-end-date').datetimepicker('getData').val() == "") {
      d2 = d1;
    } else {
      d2 = jQuery('#special-event-' + pad(i, 2) + '-end-date').datetimepicker('getDate').val();
    }
    var event = new Object();
    event.title = name;
    event.start = moment.parseZone(d1);
    event.end   = moment.parseZone(d2);
    event.editable = false; // only allow edit on the datetimepicker for these
    storeEvent( event );
  }

  //loadEvents();
}

function pad(num, size) {
  var s = num+"";
  while (s.length < size) s = "0" + s;
  return s;
}
    
var substance_units = [
    [ "Alcohol", "ml" ],
    [ "Tobacco", 'grams' ],
    [ "E-cigarettes", "min" ],
    [ "Cigars", "#" ],
    [ "Hookah", "min" ],
    [ "Blunts", "" ],
    [ "Smoked Marijuana", "" ],
    [ "Edible Marijuana", "grams"],
    [ "Fake Marijuana", "grams" ],
    [ "Marijuana oils", "grams" ],
    [ "Stimulant", "ml" ],
    [ "Cathinone", "grams" ],
    [ "Methamphetamine", "grams"],
    [ "Ecstasy", "" ],
    [ "Ketamine", "" ],
    [ "GHB", "" ],
    [ "Tranquilizers", "" ],
    [ "Heroin", "grams" ],
    [ "Pain relievers", "" ],
    [ "Cough or cold medicine", "" ],
    [ "Hallucinogen", "" ],
    [ "Liquids", "" ],
    [ "Sprays and gases", "ml" ],
    [ "Steroids", ""],
    [ "Bittamugen", "" ],
    [ "Other", "" ]
];

function getActiveSubstances() {
  var active_input_fields = jQuery('#select-substances-checkboxes input:checked');
  var active_substances = active_input_fields.map(function(a) { return jQuery(active_input_fields[a]).attr('substance'); });
  return active_substances;
}

function checkConnectionStatus() {
  jQuery.getJSON('/code/php/heartbeat.php', function() {
    //jQuery('#connection-status').addClass('connection-status-ok');
    jQuery('#connection-status').css('color', "#228B22");
    jQuery('#connection-status').attr('title', 'Connection established last at ' + Date());
  }).error(function() {
    // jQuery('#connection-status').removeClass('connection-status-ok');
    jQuery('#connection-status').css('color', "#CD5C5C");
    jQuery('#connection-status').attr('title', 'Connection failed at ' + Date());
  });
}

// calculate the special event range for this session
function updateEventRange() {
  var m = parseInt(jQuery('#session-months').val());
  var d = jQuery('#session-date-picker').data("DateTimePicker").getDate();
  // get first of this month, we don't need that if we just want to display the month range obmitting the date

  // console.log("calculate the data range for this session");
  jQuery('.session-date-range').text(  moment(d).subtract(0, 'month').format('MMM YYYY') + " to " + moment(d).subtract(m, 'month').format('MMM YYYY') );

  // tell the calendar about the first month to display
  jQuery('#calendar-loc').fullCalendar('gotoDate', moment(d));

}

function storeSubjectAndName() {
  var subject = jQuery('#session-participant').val().replace(/\s/g, '');
  var session = jQuery('#session-name').val().replace(/\s/g, '');
  jQuery('#session-participant').val(subject);
  jQuery('#session-name').val(session);
  jQuery('.subject-id').text("Subject ID: " + subject);
  jQuery('.session-id').text("Session: " + session);

  if (subject.length > 0 && session.length > 0) {
    jQuery('#session-active').text("Active Session");
    jQuery('#calendar-loc').fadeIn();
    jQuery('#open-save-session').fadeIn();
  } else {
    jQuery('#session-active').text("No Active Session");
    jQuery('#calendar-loc').fadeOut();
    jQuery('#open-save-session').fadeOut();
  }
  var active_substances = getActiveSubstances();

  var data = {
    "subjid": subject,
    "session": session,
    "act_subst": encodeURIComponent(JSON.stringify(active_substances.toArray()))
  };
  
  jQuery.get('../../code/php/session.php', data, function() {
    console.log('stored subject and session names: ' +  subject + ", " + session );
  });
}

// forget about the current session
function closeSession() {
  // just set to empty strings and submit
  jQuery('#session-participant').val("");
  jQuery('#session-name').val("");
  storeSubjectAndName();
}

function exportToCsv(filename, rows) {
    var processRow = function (row) {
	var finalVal = "\"" + row.user + "\", \"" + row.substance + "\", \"" + "\", \"" + row.amount + "\", \""
	    + row.units + "\", \"" + moment(row.start).format("MM/DD/YYYY") + "\", \""
	    + moment(row.end).format("MM/DD/YYYY") + "\"";
	return finalVal + '\n';
    };

    var csvFile = '';
    for (var i = 0; i < rows.length; i++) {
	csvFile += processRow(rows[i]);
    }

    var blob = new Blob([csvFile], { type: 'text/csv;charset=utf-8;' });
    if (navigator.msSaveBlob) { // IE 10+
	navigator.msSaveBlob(blob, filename);
    } else {
	var link = document.createElement("a");
	if (link.download !== undefined) { // feature detection
	    // Browsers that support HTML5 download attribute
	    var url = URL.createObjectURL(blob);
	    link.setAttribute("href", url);
	    link.setAttribute("download", filename);
	    link.style.visibility = 'hidden';
	    document.body.appendChild(link);
	    link.click();
	    document.body.removeChild(link);
	}
    }
}


jQuery(document).ready(function() {

      jQuery('#select-substance').on('click', 'label', function() {
	  // copy the unit over
	  jQuery('#add-event-amount').next().text(jQuery(this).find('input').attr('unit'));
	  // disable all other label
	  jQuery(this).siblings().removeClass('active');
      });
      
      jQuery('#add-event-recurring').change(function() {
	  if (jQuery('#add-event-recurring').prop('checked')) {
     	      jQuery('#recurring-details').show();
	  } else {
     	      jQuery('#recurring-details').hide();
	  }
      });

  // add the session variables to the interface
  jQuery('#user_name').text("User: " + user_name);
  jQuery('#session-participant').val(subjid);
  jQuery('#session-name').val(session);
  storeSubjectAndName();

  createCalendar();

  checkConnectionStatus();
  // Disable for now: setInterval( checkConnectionStatus, 5000 );

  jQuery('#session-participant').change(function() {
    storeSubjectAndName();
  });
  jQuery('#session-name').change(function() {
    storeSubjectAndName();
  });

  jQuery('#open-save-session').click(function() {
    jQuery('#session-participant-again').val(""); // clear the value from before
  });

  // 
  jQuery('#save-session-button').click(function() {
    // test if subjid matches
    var nameNow = jQuery('#session-participant-again').val().replace(/\s/g, '');
    var nameBefore = jQuery('#session-participant').val().replace(/\s/g, '');
    if ( nameNow != nameBefore ) {
      alert("Error: Your subject ID is not correct, please check the subject ID for correctness again.");
      return false;
    }

    // mark the session as closed


    // create spreadsheet with data
    setTimeout( (function( subject, session ) {
	// return a function
        return function() {
            var filename = user_name + "_" + subject + "_" + session + "_" + (new Date()).toLocaleString() + ".csv";
           jQuery.getJSON('code/php/events.php', function(rows) {
               exportToCsv(filename, rows);

	       // clean interface again
	       jQuery('#session-participant').val("");
	       jQuery('#session-name').val("");
	       jQuery('#select-substances-checkboxes').children().removeClass('active');
	       jQuery('#num-selected-substances').text("");
	       storeSubjectAndName();
           });
	};
    })( jQuery('#session-participant').val(), jQuery('#session-name').val() ), 1000);
 
  });
      
    // Add substances to page
    str = "";
    for (var i = 0; i < substance_units.length; i++) {
      var active = ( act_subst.indexOf( substance_units[i][0] ) < 0 ) ? "" : "active";
      str = str + "<label class=\"btn btn-default substance-checkbox\"> <input type=\"checkbox\" name=\"options\" aria-invalid=\"false\" substance=\"" 
            + substance_units[i][0] + "\" units=\"" + substance_units[i][1] + "\" "+active+">" + substance_units[i][0] + "</label>";
    }
    jQuery('#select-substances-checkboxes').append(str);
    jQuery('#select-substances-checkboxes').on('change', 'label', function() {
       // update number of selected substances
       jQuery('#num-selected-substances').text( '(' + jQuery('#select-substances-checkboxes input:checked').length + ')' );
    });

  // clear the current session setting
  // jQuery.get('../../code/php/session.php?subjid=&session=', function() {});

  jQuery('#session-date-picker').on("dp.change", function() { updateEventRange(); });
  jQuery('#session-date-picker').data("DateTimePicker").setDate(new Date());
  setTimeout( updateEventRange, 1000);
  jQuery('#session-months').change( updateEventRange );
  
  // Does this do anything?: getActiveSubstances();
  //loadEvents();
});
