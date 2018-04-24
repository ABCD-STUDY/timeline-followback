  //----------------------------------------
  // User accounts
  //----------------------------------------


  // logout the current user
  function logout() {
      if (stand_alone == 1)
	  return; // nothing to be done because user is not logged in
      
    jQuery.get('/code/php/logout.php', function(data) {
      if (data == "success") {
        // user is logged out, reload this page
      } else {
        alert('something went terribly wrong during logout: ' + data);
      }
      window.location.href = "/applications/User/login.php";
    });
  }

  numSpecialEvents = 15;

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

    //jQuery('#add-event-title').val(event.title);
    //jQuery('#add-event-substance').val(event.substance);
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

   /* for (var i = 1; i <= numSpecialEvents; i++) {
	  if (typeof jQuery('#special-event-' + pad(i,2) + '-start-date-picker').data("DateTimePicker") != 'undefined')
              jQuery('#special-event-' + pad(i,2) + '-start-date-picker').data("DateTimePicker").setDate(event.start);
	  if (typeof jQuery('#special-event-' + pad(i,2) + '-end-date-picker').data("DateTimePicker") != 'undefined')
	      jQuery('#special-event-' + pad(i,2) + '-end-date-picker').data("DateTimePicker").setDate(event.start);
    } */

    // initialize the field for the start date
    //jQuery('#add-event-start-date-picker').data("DateTimePicker").setMinDate(new Date());
    jQuery('#add-event-start-date-picker').data("DateTimePicker").setDate(event.start);

    // initialize the field for the end date
    //jQuery('#add-event-end-date-picker').data("DateTimePicker").setMinDate(new Date());
    jQuery('#add-event-end-date-picker').data("DateTimePicker").setDate(event.end);

    // highlight the substance
    jQuery('#select-substance-radio-group label').removeClass('active');
      jQuery('#select-substance-radio-group input').each(function() {
	  if (jQuery(this).attr('substance') == event.substance) {
	      jQuery(this).parent().addClass('active');
              jQuery('#add-event-amount').next().text(jQuery(this).attr('unit'));	      
	  }
      });

    //jQuery('#select-substance-radio-group input').prop('checked', false);
    //jQuery('#select-substance-radio-gropu label').prop('active', false);
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
      '&title=' + encodeURIComponent(event.title) +
      '&start=' + encodeURIComponent(s) +
      '&end=' + encodeURIComponent(e) +
      '&substance=' + encodeURIComponent(event.substance) +
      '&amount=' + encodeURIComponent(event.amount) +
      '&color=' + encodeURIComponent(event.color) +
      '&unit=' + encodeURIComponent(event.unit));

    // send the url to create the event
    jQuery.getJSON(url, function(data) {

      // if the response is ok
      if (data.ok == 1) {
        // check if an event id was defined
        if (typeof(data.eid) !== 'undefined') {
          // set the event id
          event.eid = data.eid;
          // render the event to the calendar (this introduced a duplicate event), event still appears on calendar without this line
          //jQuery('#calendar-loc').fullCalendar('renderEvent', event, true);
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
      '&title=' + encodeURIComponent(event.title) +
      '&start=' + encodeURIComponent(event.start.format()) +
      '&end=' + encodeURIComponent(event.end.format()) +
      '&eid=' + encodeURIComponent(event.eid));

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
      '&title=' + encodeURIComponent(event.title) +
      '&start=' + encodeURIComponent(s) +
      '&end=' + encodeURIComponent(e) +
      '&eid=' + encodeURIComponent(event.eid) +
      '&substance=' + encodeURIComponent(event.substance) +
      '&amount=' + encodeURIComponent(event.amount) +
      '&unit=' + encodeURIComponent(event.units) +
      '&color=' + encodeURIComponent(event.color));

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

    jQuery.getJSON('code/php/events.php?action=mark&status=start&user_name='+user_name, function(data) {
	console.log(data);
    });

    storeSubjectAndName();
    // update the calendar and display all special events
    createCalendar();
  });

  var selectedSubstance;
  var selectedUnits;
  var selectedIndex = 0;

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

    ev.user      = user_name;
    ev.fullDay   = jQuery('#add-event-fullday').prop('checked');  
    ev.substance = jQuery('#select-substance-radio-group label.active').find('input').attr('substance'); // selectedSubstance;
    ev.units     = jQuery('#select-substance-radio-group label.active').find('input').attr('unit'); //  selectedUnits;
    ev.amount    = jQuery('#add-event-amount').val();
    ev.title     = ev.substance + ' (' + ev.amount + ' ' + ev.units + ')';
    ev.editable  = true;

    // only allow to save an event if we have both substance and amount
    if (typeof ev.substance == 'undefined') {
       alert("Error: no substance specified");
       return false;
    }
    if (ev.amount == "") {
       alert("Error: no amount specified");
       return false;
    }
      
    var su = jQuery('#select-substance-radio-group label').toArray();
    for (var i = 0; i < su.length; i++) {
        if (jQuery(su[i]).find('input').attr('substance') == ev.substance) {
          selectedIndex = i;
        }
    }
    selectedIndex = selectedIndex % colors.length; 
    ev.color      = colors[selectedIndex];  

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
    ev.unit  = jQuery('#add-event-amount').next().text();

    if (typeof(ev.eid) !== 'undefined') {
      if (!updateEvent(ev)) {
        jQuery('#calendar-loc').fullCalendar('refetchEvents');
      }
    } else {
	// If we have a multiple day event - split the event into separate days.
	// This split is specific to the timeline followback implementation.

	// we also need to use the highlighted days of the week if the event is marked recurring
	var markedDaysOfWeek = [ 0, 1, 2, 3, 4, 5, 6 ];
	if (jQuery('#add-event-recurring').prop('checked')) {
	    markedDaysOfWeek = jQuery('#add-event-days-of-week input:checked').map(function(a) { return parseInt(jQuery(this).attr('dayOfWeek')); }).toArray();
	}
	
	var a = ev.start.clone().startOf('day');
	var o = ev.end.clone().startOf('day');
	var sendOne = false;
	do {
	    if (markedDaysOfWeek.indexOf(a.weekday()) == -1) { // day not in marked days of week
		continue;
	    }
	    var evN = ev;
	    evN.start = a;
	    evN.end = a;
	    storeEvent(evN);
	    //if (!storeEvent(evN)) {
	    //	jQuery('#calendar-loc').fullCalendar('refetchEvents');
            //}
	    sendOne = true;
        } while( a.add(1, 'days').diff(o) < 0);
	if (sendOne) {
	    // do we need this?
	    jQuery('#calendar-loc').fullCalendar('refetchEvents');
	}
	
	//if (!storeEvent(ev)) {
        //    jQuery('#calendar-loc').fullCalendar('refetchEvents');
	//}
    }
  });

  // required to display the date and time picker
  jQuery('#session-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  for (var i = 1; i <= numSpecialEvents; i++) {
      jQuery('#special-event-' + pad(i,2) + '-start-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
      jQuery('#special-event-' + pad(i,2) + '-end-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  }
  jQuery('#add-event-start-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
  jQuery('#add-event-end-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });

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

function addEventActiveSubstances( active_substances ) {
    jQuery('#select-substance-radio-group').children().remove();
    for(var i = 0; i < active_substances.length; i++) {
	// a substance can have more than one dose, create a button group for each substance that has multiple doses
	if (active_substances[i][1].split(":").length > 1) { // found multi-dose substance
	    var ll = active_substances[i][1].split(":");
	    for (var j = 0; j < ll.length; j++) {
  		jQuery('#select-substance-radio-group').append("<label class=\"btn btn-default substance-checkbox\"> <input type=\"checkbox\" name=\"options\" aria-invalid=\"false\" substance=\"" + active_substances[i][0] + "\" unit=\"" + ll[j] + "\">" + active_substances[i][0] + " " + "<span class=\"tiny\">" + ll[j] +  "</span></label>");
	    }
	} else { // found single dose substance	
	    // jQuery('#substance-list').append("<li><a class=\"substance-selection\">" + active_substances[i] + "</a></li>");
	    jQuery('#select-substance-radio-group').append("<label class=\"btn btn-default substance-checkbox\"> <input type=\"checkbox\" name=\"options\" aria-invalid=\"false\" substance=\"" + active_substances[i][0] + "\" unit=\"" + active_substances[i][1] + "\">" + active_substances[i][0] + "</label>");
	}
    }
}

// setup the calendar
function createCalendar() {

  var active_substances = getActiveSubstances();
  addEventActiveSubstances( active_substances );

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

      // do not display the time in the event title
      timeFormat: '',

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

      // add jquery.ui.touch.js
      //eventRender: function(event, element) {
      //   jQuery(element).addTouch();
      //},
	
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
          start: start,
          end: end,
          fullDay: fullDay
        };
        jQuery('#calendar-loc').fullCalendar('unselect');
        jQuery('#add-event-amount').val("");
        jQuery('#add-event-recurring').prop('checked', false);
        specifyEvent( eventData );
      },
	eventSources: [ "code/php/events.php", {
	    color: 'white',
	    textColor: 'black',
	    events: [
		{ start: '2015-12-21', title: 'Start Christmas holidays' },
		{ start: '2017-12-22', title: 'Start Christmas holidays' },

		{ start: '2016-01-01', title: 'End Christmas holidays' },
		{ start: '2017-01-01', title: 'End Christmas holidays' },

		{ start: '2016-02-15', title: 'Start Winter holidays' },
		{ start: '2017-12-20', title: 'Start Winter holidays' },

		{ start: '2016-02-19', title: 'End Winter holidays' },
		{ start: '2018-01-02', title: 'End Winter holidays' },

		{ start: '2016-03-25', title: 'Start Easter holidays' },
		{ start: '2018-03-30', title: 'Start Easter holidays' },
		{ start: '2019-04-19', title: 'Start Easter holidays' },
		{ start: '2020-04-10', title: 'Start Easter holidays' },

		{ start: '2016-04-08', title: 'End Easter holidays' },
		{ start: '2018-04-02', title: 'End Easter holidays' },
		{ start: '2019-04-22', title: 'End Easter holidays' },
		{ start: '2020-04-13', title: 'End Easter holidays' },

		{ start: '2016-05-30', title: 'Start Spring holidays' },
		{ start: '2017-05-30', title: 'Start Spring holidays' },

		{ start: '2016-06-03', title: 'End Spring holidays' },
		{ start: '2016-06-20', title: 'Start Summer holidays' },
		{ start: '2016-08-31', title: 'End Summer holidays' },
		{ start: '2016-10-24', title: 'Start Autumn holidays' },
		{ start: '2016-10-28', title: 'End Autumn holidays' },
		{ start: '2016-12-19', title: 'Start Christmas holidays' },
		{ start: '2017-01-02', title: 'End Christmas holidays' },
		
		{ start: '2016-01-01', title: 'New Year\'s Day' },
		{ start: '2017-01-01', title: 'New Year\'s Day' },
		{ start: '2018-01-01', title: 'New Year\'s Day' },
		{ start: '2019-01-01', title: 'New Year\'s Day' },

		{ start: '2016-01-18', title: 'Martin Luther King Day' },
		{ start: '2017-01-16', title: 'Martin Luther King Day' },

		{ start: '2016-02-08', title: 'Chinese New Year' },
		{ start: '2017-01-28', title: 'Chinese New Year' },
		{ start: '2018-02-16', title: 'Chinese New Year' },

		{ start: '2016-02-14', title: 'Valentine\'s Day' },
		{ start: '2017-02-14', title: 'Valentine\'s Day' },
		
		{ start: '2016-02-15', title: 'Presidents\' Day' },
		{ start: '2017-02-20', title: 'Presidents\' Day' },

		{ start: '2016-04-18', title: 'Patriot\'s Day' },
		{ start: '2017-04-17', title: 'Patriot\'s Day' },

		{ start: '2016-03-13', title: 'Daylight Saving Time starts' },
		{ start: '2017-03-12', title: 'Daylight Saving Time starts' },
		{ start: '2016-11-06', title: 'Daylight Saving Time ends' },
		{ start: '2017-11-05', title: 'Daylight Saving Time ends' },

		{ start: '2016-03-17', title: 'St. Patrick\'s Day' },
		{ start: '2017-03-17', title: 'St. Patrick\'s Day' },

		{ start: '2016-03-27', title: 'Easter Sunday' },
		{ start: '2016-03-28', title: 'Easter Monday' },

		{ start: '2016-03-31', title: 'César Chávez Day' },
		{ start: '2017-03-31', title: 'César Chávez Day' },

		{ start: '2016-04-23', title: 'Passover (first day)' },
		{ start: '2017-04-10', title: 'Passover (first day)' },

		{ start: '2016-04-28', title: 'Take our Daughters and Sons to Work Day' },
		{ start: '2017-04-26', title: 'Take our Daughters and Sons to Work Day' },

		{ start: '2016-04-29', title: 'Orthodox Good Friday' },
		{ start: '2017-04-14', title: 'Orthodox Good Friday' },
		{ start: '2018-04-06', title: 'Orthodox Good Friday' },
		{ start: '2019-04-26', title: 'Orthodox Good Friday' },

		{ start: '2016-04-30', title: 'Last Day of Passover' },
		{ start: '2017-04-18', title: 'Last Day of Passover' },

		{ start: '2016-04-30', title: 'Orthodox Holy Saturday' },
		{ start: '2016-05-01', title: 'Orthodox Easter' },

		{ start: '2016-05-05', title: 'Cinco de Mayo' },
		{ start: '2017-05-05', title: 'Cinco de Mayo' },

		{ start: '2016-05-08', title: 'Mother\'s Day' },
		{ start: '2017-05-14', title: 'Mother\'s Day' },

		{ start: '2016-05-30', title: 'Memorial Day' },
		{ start: '2017-05-29', title: 'Memorial Day' },

		{ start: '2016-06-07', title: 'Ramadan starts' },
		{ start: '2017-05-26', title: 'Ramadan starts' },

		{ start: '2016-06-19', title: 'Father\'s Day' },
		{ start: '2017-06-18', title: 'Father\'s Day' },
		
		{ start: '2016-07-04', title: 'Independence Day' },
		{ start: '2017-07-04', title: 'Independence Day' },

		{ start: '2016-09-05', title: 'Labor Day' },
		{ start: '2017-09-04', title: 'Labor Day' },

		{ start: '2016-10-03', title: 'Rosh Hashana' },
		{ start: '2017-09-20', title: 'Rosh Hashana' },
		
		{ start: '2016-10-12', title: 'Yom Kippur' },
		{ start: '2017-09-29', title: 'Yom Kippur' },

		{ start: '2016-10-31', title: 'Halloween' },
		{ start: '2017-10-31', title: 'Halloween' },

		{ start: '2016-11-11', title: 'Veterans Day' },
		{ start: '2017-11-11', title: 'Veterans Day' },

		{ start: '2016-11-24', title: 'Thanksgiving Day' },
		{ start: '2016-11-25', title: 'Presidents\' Day' },
		
		{ start: '2016-11-25', title: 'Black Friday' },
		{ start: '2017-11-24', title: 'Black Friday' },

		{ start: '2016-11-28', title: 'Cyber Monday' },
		{ start: '2017-11-27', title: 'Cyber Monday' },

		{ start: '2016-12-06', title: 'St Nicholas\' Day' },
		{ start: '2017-12-06', title: 'St Nicholas\' Day' },
		
		{ start: '2016-12-24', title: 'Christmas Eve' },
		{ start: '2017-12-24', title: 'Christmas Eve' },

		{ start: '2016-12-25', title: 'Chanukah/Hanukkah (first day)' },
		{ start: '2017-12-25', title: 'Chanukah/Hanukkah (first day)' },

		{ start: '2016-12-25', title: 'Christmas Day' },
		{ start: '2017-12-25', title: 'Christmas Day' },

		{ start: '2016-12-26', title: 'Kwanzaa (until Jan 1)' },
		{ start: '2017-12-26', title: 'Kwanzaa (until Jan 1)' },
		
		{ start: '2016-03-24', title: 'Purim' },
		{ start: '2017-03-11', title: 'Purim' },

		{ start: '2016-12-30', title: 'New Year\'s Eve observed' },
		{ start: '2017-12-31', title: 'New Year\'s Eve observed' },

		{ start: '2016-12-31', title: 'New Year\'s Eve' },
		{ start: '2017-12-31', title: 'New Year\'s Eve' }
            ]
	}]

    });
  }

  // collect the current list of special events and add to the calendar (if they don't exist already)
  for (var i = 1; i <= numSpecialEvents; i++) {
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
  jQuery('#calendar-loc').fullCalendar('refetchEvents');    
}

function pad(num, size) {
  var s = num+"";
  while (s.length < size) s = "0" + s;
  return s;
}
    
var substance_units = [
    [ "Alcohol", "standard drinks" ],
    [ "Tobacco smoked", "cigarettes" ],
    [ "Nicotine replacement", "doses" ],
    [ "E-cigarettes", "occasions" ],
    [ "Tobacco chew", "pinches"],
    [ "Cigars", "cigars" ],
    [ "Hookah", "hits" ],
    [ "Pipe Tobacco", "hits" ],
    [ "Blunts", "grams" ],
    [ "Smoked MJ", "grams" ],
    [ "Edible MJ", [ "mg THC", "occasions" ] ],
    [ "Fake MJ", "grams" ],
    [ "MJ concentrates", [ "mg", "occasions" ] ],
    [ "MJ infused alcohol drinks", "standard drinks"],
    [ "MJ tincture", "ml"],
    [ "Magic mushrooms", "occasions"],
    [ "Saliva", "occasions"],
    [ "Cocaine", "occasions" ],
    [ "Stimulant medication", "pills" ],
    [ "Cathinones", "occasions" ],
    [ "Methamphetamine", "occasions"],
    [ "Ecstasy", "tablets" ],
    [ "Ketamine", "occasions" ],
    [ "GHB", "occasions" ],
    [ "Tranquilizers or sedatives", "pills" ],
    [ "Heroin", "occasions" ],
    [ "Pain relievers", "pills" ],
    [ "Cough or cold medicine", "occasions" ],
    [ "Hallucinogens", "occasions" ],
    [ "Inhalants", "occasions" ],
    [ "Steroids", "occasions"],
    [ "Bittamugen", "occasions" ],
    [ "Other", "" ]
];

function getActiveSubstances() {
  var active_input_fields = jQuery('#select-substances-checkboxes input:checked');
  var active_substances = active_input_fields.map(function(a) { return [[ jQuery(active_input_fields[a]).attr('substance'), jQuery(active_input_fields[a]).attr('units') ]] });
  return active_substances;
}

function checkConnectionStatus() {
    if (!stand_alone) {
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
  var subject = jQuery('#session-participant').val();
  var session = jQuery('#session-name').val();
  var run     = jQuery('#session-run').val();
  jQuery('#session-participant').val(subject);
  jQuery('#session-name').val(session);
  jQuery('.subject-id').text("Subject ID: " + subject);
  jQuery('.session-id').text("Session: " + session);
  jQuery('.run-id').text("Run: " + run);

  if (subject !== null && subject.length > 0 && session !== null && session.length > 0) {
    jQuery('#session-active').text("Active Session");
    jQuery('#calendar-loc').fadeIn();
    jQuery('#open-save-session').fadeIn();
    jQuery('#cancel-session-button').fadeIn();
    jQuery('#new-session-button').fadeOut();
  } else {
    jQuery('#session-active').text("No Active Session");
    jQuery('#calendar-loc').fadeOut();
    jQuery('#open-save-session').fadeOut();
    jQuery('#cancel-session-button').fadeOut();
    jQuery('#new-session-button').fadeIn();
  }

  var active_substances = getActiveSubstances();

  var data = {
    "subjid": subject,
    "sessionid": session,
    "run": run,
    "act_subst": encodeURIComponent(JSON.stringify(active_substances.toArray())),
    "task": "timeline-followback"
  };

  url = "../../code/php/session.php";
  if (stand_alone) {
     url = "code/php/session.php";
  }
  jQuery.get(url, data, function() {
      console.log('stored subject,session, act_subst, and run: ' +  subject + ", " + session + ", " + encodeURIComponent(JSON.stringify(active_substances.toArray())) + ", " + run);
  });
}

// forget about the current session
function closeSession() {
  // just set to empty strings and submit
  jQuery('#session-participant').val("");
  jQuery('#session-name').val("");
  jQuery('#select-substances-checkboxes').children().removeClass('active');
  jQuery('#select-substance-radio-group').children().remove();
  jQuery('#num-selected-substances').text("");
  jQuery('#session-run').val("01");  
  storeSubjectAndName();
}

function exportToCsv(filename, rows) {
    var processRow = function (row) {
	if (row.substance == "undefined") {
	    row.substance = "";
	} else {
            row.substance = "\"" + row.substance + "\"";
	}
	if (row.amount == "undefined") {
	    row.amount = "";
	}
	if (row.unit == "undefined") {
	    row.unit = "";
	} else {
	    row.unit = "\"" + row.unit + "\"";
	}
	var finalVal = user_name + ",\"" + row.title + "\"," + row.substance + "," + row.amount + ","
	    + row.unit + "," + moment(row.start).format("MM/DD/YYYY") + ","
	    + moment(row.end).format("MM/DD/YYYY");
	return finalVal + '\n';
    };
    
    var csvFile = 'user name, title, substance, amount, unit, date (start), date (end)\n';
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

function getSessionNamesFromLocalFile() {
    jQuery.getJSON('session_names.json', function(data) {
	for (var i = 0; i < data.length; i++) {
	    val = "";
	    if (i == 1) {
		val = "selected=\"selected\"";
	    }
	    jQuery('#session-name').append("<option " + val + " value=\"" + data[i].unique_event_name + "\">" + data[i].event_name + "</option>");
	}
	getParticipantNamesFromLocalFile();
    });
}

// get valid session names
function getSessionNamesFromREDCap() {
    jQuery.getJSON('/code/php/getRCEvents.php', function(data) {
	for (var i = 0; i < data.length; i++) {
	    val = "";
	    if (i == 1) {
		val = "selected=\"selected\"";
	    }
	    jQuery('#session-name').append("<option " + val + " value=\"" + data[i].unique_event_name + "\">" + data[i].event_name + "</option>");
	}
	getParticipantNamesFromREDCap();
	//storeSubjectAndName();
    });
}

    function getParticipantNamesFromLocalFile() {
	jQuery.getJSON('participants.json', function(data) {
	    for (var i = 0; i < data.length; i++) {
		jQuery('#session-participant').append("<option value=\"" + data[i] + "\">" + data[i] + "</option>");
 	    }
	    // make sure we don't have selected a name here (only value in subjid counts at the beginning)
	    jQuery('#session-participant').select2({ placeholder: "Select a pGUID" });
	    jQuery('#session-participant').val(subjid);
	    storeSubjectAndName();
	});
    }
    
function getParticipantNamesFromREDCap() {
    jQuery.getJSON('/code/php/getParticipantNamesFromREDCap.php', function(data) {
	for (var i = 0; i < data.length; i++) {
	    jQuery('#session-participant').append("<option value=\"" + data[i] + "\">" + data[i] + "</option>");
	}
	// make sure we don't have selected a name here (only value in subjid counts at the beginning)
	jQuery('#session-participant').select2({ placeholder: "Select a pGUID" });
	jQuery('#session-participant').val("").trigger('change');
	//jQuery('#session-participant').val(subjid);
	storeSubjectAndName();
    });
}

function addSpecialEventsInterface( num ) {
    for( var i = 1; i <= num; i++) {
	jQuery('#sessions-table tbody').append(
	    '<tr>' +
                '<td style="width: 33%;"><input type="text" class="form-control" id="special-event-' + pad(i,2) + '-name" placeholder="Event name"></td>' +
                '<td>' +
                '  <div class="input-group date" id="special-event-' + pad(i,2) + '-start-date-picker">' +
                '     <input type="text" data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-' + pad(i,2) + '-start-date" class="form-control" />' +
                '             <span class="input-group-addon">' +
                '             <span class="glyphicon glyphicon-calendar"></span>' +
                '             </span>' +
                '  </div>' +
                '</td>' +
                '<td>' +
                '  <div class="input-group date" id="special-event-' + pad(i,2) + '-end-date-picker">' +
                '     <input type="text" data-format="MM/dd/yyyy HH:mm:ss PP" id="special-event-' + pad(i,2) + '-end-date" class="form-control" />' +
                '             <span class="input-group-addon">' +
                '             <span class="glyphicon glyphicon-calendar"></span>' +
                '             </span>' +
                '  </div>' +
                '</td></tr>');
    }
    for (var i = 1; i <= numSpecialEvents; i++) {
	jQuery('#special-event-' + pad(i,2) + '-start-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });
	jQuery('#special-event-' + pad(i,2) + '-end-date-picker').datetimepicker({language: 'en', format: "MM/DD/YYYY" });

	// add a callback that makes this a single day (if start changes, copy to end if end is empty)
	jQuery('#special-event-' + pad(i,2) + '-start-date').on('change', (function(start, end) {
	    return function() {
		console.log("in event " + start + " " + end);
		if (jQuery(end).val() == "") { // if we don't have a date yet, copy the start date over
		    jQuery(end).val(jQuery(start).val());
		}
	    };
	})(jQuery('#special-event-' + pad(i,2) + '-start-date'), jQuery('#special-event-' + pad(i,2) + '-end-date')));
    }
}

var colors = [ "#C6CAED", "#ADA8BE", "#A28497", "#6F5E5C", "#4A5240" ];

jQuery(document).ready(function() {

    jQuery('#add-event-amount').on('change', function(e) {
        // this should only happen for occasions, otherwise allow float
        var unit = jQuery('#add-event-amount').next().text();
        var v = jQuery('#add-event-amount').val();
        if (v == "") {
            return; // nothing to do
        }
        if (unit == "occasions") {
            v = parseInt(v);
        } else {
            v = parseFloat(v);
        }
        jQuery('#add-event-amount').val(v);
    });
    
    // add special events section to interface
    addSpecialEventsInterface(numSpecialEvents);

    if (stand_alone == true) {
	getSessionNamesFromLocalFile();
    } else {
	getSessionNamesFromREDCap();
    }

  // add the session variables to the interface
  jQuery('#user_name').text("User: " + user_name);
  jQuery('#session-participant').val(subjid);
  jQuery('#session-name').val(session);
  jQuery('#session-run').val(run);
    
  // convert the 2D array of active substance names and units into a 1D array of substance names
  var act_subst_names = [];
  for (var i = 0; i < act_subst.length; i++) {
    act_subst_names.push(act_subst[i][0]);
  }

  // for each substance, create a checkbox button
  // if the substance is an active substance, then set the label as active
  str = "";
  for (var i = 0; i < substance_units.length; i++) {
      var active = ( act_subst_names.indexOf( substance_units[i][0] ) < 0 ) ? "" : "active";
      var checked = (active) ? "checked" : "";
      var su = substance_units[i][1];
      if (! (typeof substance_units[i][1] === 'string')) {
         su = substance_units[i][1].map(function(a) { return a.replace(/:/g, "_"); } ).join(":");
      }
      str = str + "<label class=\"btn btn-default substance-checkbox "
            + active + "\"> <input type=\"checkbox\" name=\"options\" aria-invalid=\"false\" substance=\"" 
            + substance_units[i][0] + "\" units=\"" + su
            + "\"" + checked + ">" + substance_units[i][0] + "</label>";
  }

  jQuery('#select-substances-checkboxes').append(str);
  jQuery('#select-substances-checkboxes').on('change', 'label', function() {
     // update number of selected substances
     jQuery('#num-selected-substances').text( '(' + jQuery('#select-substances-checkboxes input:checked').length + ')' );
  });

  jQuery('#select-substance-radio-group').on('click', 'label', function() {
      // copy the unit over
      jQuery('#add-event-amount').next().text(jQuery(this).find('input').attr('unit'));
      // disable all other label
      jQuery(this).siblings().removeClass('active');
      // trigger a change event on the amount (in case there was something in there arealdy and we need to switch from float to int
      jQuery('#add-event-amount').trigger('change');
      
      // store the selected substance and units
      selectedSubstance = jQuery(this).find('input').attr('substance');
      selectedUnits = jQuery(this).find('input').attr('unit');
      selectedIndex = jQuery('#select-substance-radio-group label').toArray().indexOf(jQuery(this).toArray()[0]); // the index of the selected substance is used as color later
      selectedIndex = selectedIndex % colors.length; 
      // console.log("index is: " + selectedIndex);
  });
    
  jQuery('#add-event-recurring').change(function() {
    if (jQuery('#add-event-recurring').prop('checked')) {
      jQuery('#recurring-details').show();
      jQuery('#add-event-days-of-week').show();
    } else {
      jQuery('#recurring-details').hide();
      jQuery('#add-event-days-of-week').hide();
    }
  });
    
  createCalendar();

  checkConnectionStatus();
  // Disable for now:
  setInterval( checkConnectionStatus, 5000 );

  jQuery('#session-participant').change(function() {
    storeSubjectAndName();
  });
  jQuery('#session-name').change(function() {
    storeSubjectAndName();
  });
  jQuery('#session-run').change(function() {
    storeSubjectAndName();
  });
  jQuery('#select-substances-checkboxes').on('change', 'label', function() {
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
    jQuery.getJSON('code/php/events.php?action=mark&status=closed&user_name='+user_name, function(data) {
	console.log(data);
    });

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
          jQuery('#select-substance-radio-group').children().remove();
          jQuery('#num-selected-substances').text("");
          storeSubjectAndName();
        });
      };
    })( jQuery('#session-participant').val(), jQuery('#session-name').val() ), 1000);
 
  });

  // clear the current session setting
  // jQuery.get('../../code/php/session.php?subjid=&session=', function() {});

  jQuery('#session-date-picker').on("dp.change", function() { updateEventRange(); });
  jQuery('#session-date-picker').data("DateTimePicker").setDate(new Date());
  setTimeout( updateEventRange, 1000);
  jQuery('#session-months').change( updateEventRange );

});
