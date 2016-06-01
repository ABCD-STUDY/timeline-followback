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

  numSpecialEvents = 3;

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

    for (var i = 1; i <= numSpecialEvents; i++) {
        jQuery('#special-event-' + pad(i,2) + '-start-date-picker').data("DateTimePicker").setDate(event.start);
	jQuery('#special-event-' + pad(i,2) + '-end-date-picker').data("DateTimePicker").setDate(event.start);
    }

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
		{ start: '2016-01-01', title: 'New Year\'s Day' },
		{ start: '2016-01-06', title: 'Epiphany' },
		{ start: '2016-01-07', title: 'Orthodox Christmas Day' },
		{ start: '2016-01-13', title: 'Stephen Foster Memorial Day' },
		{ start: '2016-01-14', title: 'Orthodox New Year' },
		{ start: '2016-01-15', title: 'Lee Jackson Day' },
		{ start: '2016-01-18', title: 'Martin Luther King Day' },
		{ start: '2016-01-18', title: 'Robert E Lee\'s Birthday' },
		{ start: '2016-01-18', title: 'State Holiday' },
		{ start: '2016-01-18', title: 'Idaho Human Rights Day' },
		{ start: '2016-01-18', title: 'Civil Rights Day' },
		{ start: '2016-01-19', title: 'Robert E Lee\'s Birthday' },
		{ start: '2016-01-19', title: 'State Holiday' },
		{ start: '2016-01-25', title: 'Tu Bishvat/Tu B\'Shevat' },
		{ start: '2016-01-29', title: 'Kansas Day' },
		{ start: '2016-02-01', title: 'National Freedom Day' },
		{ start: '2016-02-02', title: 'Groundhog Day' },
		{ start: '2016-02-04', title: 'Rosa Parks Day' },
		{ start: '2016-02-05', title: 'National Wear Red Day' },
		{ start: '2016-02-08', title: 'Chinese New Year' },
		{ start: '2016-02-09', title: 'Shrove Tuesday/Mardi Gras' },
		{ start: '2016-02-10', title: 'Ash Wednesday' },
		{ start: '2016-02-12', title: 'Lincoln\'s Birthday' },
		{ start: '2016-02-14', title: 'Valentine\'s Day' },
		{ start: '2016-02-14', title: 'Statehood Day in Arizona' },
		{ start: '2016-02-15', title: 'Presidents\' Day' },
		{ start: '2016-02-15', title: 'Daisy Gatson Bates Day' },
		{ start: '2016-02-15', title: 'Susan B Anthony\'s Birthday' },
		{ start: '2016-02-28', title: 'Linus Pauling Day' },
		{ start: '2016-03-01', title: 'St. David\'s Day' },
		{ start: '2016-03-01', title: 'Town Meeting Day Vermont' },
		{ start: '2016-03-02', title: 'Texas Independence Day' },
		{ start: '2016-03-02', title: 'Read Across America Day' },
		{ start: '2016-03-04', title: 'Employee Appreciation Day' },
		{ start: '2016-03-07', title: 'Casimir Pulaski Day' },
		{ start: '2016-03-13', title: 'Daylight Saving Time starts' },
		{ start: '2016-03-17', title: 'St. Patrick\'s Day' },
		{ start: '2016-03-17', title: 'Evacuation Day' },
		{ start: '2016-03-20', title: 'Palm Sunday' },
		{ start: '2016-03-20', title: 'March equinox' },
		{ start: '2016-03-24', title: 'Maundy Thursday' },
		{ start: '2016-03-24', title: 'Purim' },
		{ start: '2016-03-25', title: 'Good Friday' },
		{ start: '2016-03-25', title: 'Maryland Day' },
		{ start: '2016-03-25', title: 'Prince Jonah Kuhio Kalanianaoles dag observed' },
		{ start: '2016-03-26', title: 'Holy Saturday' },
		{ start: '2016-03-26', title: 'Prince Jonah Kuhio Kalanianaoles dag' },
		{ start: '2016-03-27', title: 'Easter Sunday' },
		{ start: '2016-03-28', title: 'Easter Monday' },
		{ start: '2016-03-28', title: 'Seward\'s Day' },
		{ start: '2016-03-31', title: 'César Chávez Day' },
		{ start: '2016-04-01', title: 'Pascua Florida Day observed' },
		{ start: '2016-04-02', title: 'Pascua Florida Day' },
		{ start: '2016-04-06', title: 'National Tartan Day' },
		{ start: '2016-04-12', title: 'National Library Workers\' Day' },
		{ start: '2016-04-13', title: 'Thomas Jefferson\'s Birthday' },
		{ start: '2016-04-15', title: 'Father Damien Day' },
		{ start: '2016-04-15', title: 'Emancipation Day observed' },
		{ start: '2016-04-16', title: 'Emancipation Day' },
		{ start: '2016-04-18', title: 'Tax Day' },
		{ start: '2016-04-18', title: 'Patriot\'s Day' },
		{ start: '2016-04-21', title: 'San Jacinto Day' },
		{ start: '2016-04-22', title: 'Oklahoma Day' },
		{ start: '2016-04-23', title: 'Passover (first day)' },
		{ start: '2016-04-25', title: 'Confederate Memorial Day' },
		{ start: '2016-04-25', title: 'State Holiday' },
		{ start: '2016-04-25', title: 'State Holiday' },
		{ start: '2016-04-26', title: 'State Holiday' },
		{ start: '2016-04-27', title: 'Administrative Professionals Day' },
		{ start: '2016-04-28', title: 'Take our Daughters and Sons to Work Day' },
		{ start: '2016-04-29', title: 'Orthodox Good Friday' },
		{ start: '2016-04-29', title: 'Arbor Day' },
		{ start: '2016-04-30', title: 'Last Day of Passover' },
		{ start: '2016-04-30', title: 'Orthodox Holy Saturday' },
		{ start: '2016-05-01', title: 'Orthodox Easter' },
		{ start: '2016-05-01', title: 'Law Day' },
		{ start: '2016-05-01', title: 'Loyalty Day' },
		{ start: '2016-05-02', title: 'Orthodox Easter Monday' },
		{ start: '2016-05-03', title: 'Primary Election Day Indiana' },
		{ start: '2016-05-04', title: 'Yom HaShoah' },
		{ start: '2016-05-04', title: 'Kent State Shootings Remembrance' },
		{ start: '2016-05-04', title: 'Rhode Island Independence Day' },
		{ start: '2016-05-05', title: 'Ascension Day' },
		{ start: '2016-05-05', title: 'Isra and Mi\'raj' },
		{ start: '2016-05-05', title: 'Cinco de Mayo' },
		{ start: '2016-05-05', title: 'National Day of Prayer' },
		{ start: '2016-05-06', title: 'National Nurses Day' },
		{ start: '2016-05-07', title: 'National Explosive Ordnance Disposal (EOD) Day' },
		{ start: '2016-05-08', title: 'Mother\'s Day' },
		{ start: '2016-05-08', title: 'Truman Day' },
		{ start: '2016-05-09', title: 'Truman Day observed' },
		{ start: '2016-05-10', title: 'State Holiday' },
		{ start: '2016-05-10', title: 'State Holiday' },
		{ start: '2016-05-10', title: 'Primary Election Day West Virginia' },
		{ start: '2016-05-12', title: 'Yom Ha\'atzmaut' },
		{ start: '2016-05-15', title: 'Pentecost' },
		{ start: '2016-05-15', title: 'Peace Officers Memorial Day' },
		{ start: '2016-05-16', title: 'Whit Monday' },
		{ start: '2016-05-20', title: 'National Defense Transportation Day' },
		{ start: '2016-05-21', title: 'Armed Forces Day' },
		{ start: '2016-05-22', title: 'Trinity Sunday' },
		{ start: '2016-05-22', title: 'National Maritime Day' },
		{ start: '2016-05-22', title: 'Harvey Milk Day' },
		{ start: '2016-05-25', title: 'Emergency Medical Services for Children Day' },
		{ start: '2016-05-25', title: 'National Missing Children\'s Day' },
		{ start: '2016-05-26', title: 'Corpus Christi' },
		{ start: '2016-05-26', title: 'Lag BaOmer' },
		{ start: '2016-05-30', title: 'Memorial Day' },
		{ start: '2016-05-30', title: 'Jefferson Davis Birthday' },
		{ start: '2016-06-01', title: 'Statehood Day' },
		{ start: '2016-06-03', title: 'Jefferson Davis Birthday' },
		{ start: '2016-06-06', title: 'Jefferson Davis Birthday' },
		{ start: '2016-06-06', title: 'D-Day' },
		{ start: '2016-06-07', title: 'Ramadan starts' },
		{ start: '2016-06-10', title: 'Kamehameha Day observed' },
		{ start: '2016-06-11', title: 'Kamehameha Day' },
		{ start: '2016-06-12', title: 'Shavuot' },
		{ start: '2016-06-14', title: 'U.S. Army Birthday' },
		{ start: '2016-06-14', title: 'Flag Day' },
		{ start: '2016-06-17', title: 'Bunker Hill Day' },
		{ start: '2016-06-19', title: 'Father\'s Day' },
		{ start: '2016-06-19', title: 'Juneteenth' },
		{ start: '2016-06-19', title: 'Emancipation Day' },
		{ start: '2016-06-20', title: 'June Solstice' },
		{ start: '2016-06-20', title: 'West Virginia Day' },
		{ start: '2016-06-20', title: 'American Eagle Day' },
		{ start: '2016-07-02', title: 'Lailat al-Qadr' },
		{ start: '2016-07-04', title: 'Independence Day' },
		{ start: '2016-07-07', title: 'Eid al-Fitr' },
		{ start: '2016-07-24', title: 'Pioneer Day' },
		{ start: '2016-07-24', title: 'Parents\' Day' },
		{ start: '2016-07-25', title: 'Pioneer Day observed' },
		{ start: '2016-08-01', title: 'Colorado Day' },
		{ start: '2016-08-04', title: 'U.S. Coast Guard Birthday' },
		{ start: '2016-08-07', title: 'Purple Heart Day' },
		{ start: '2016-08-08', title: 'Victory Day' },
		{ start: '2016-08-14', title: 'Tisha B\'Av' },
		{ start: '2016-08-15', title: 'Assumption of Mary' },
		{ start: '2016-08-16', title: 'Bennington Battle Day' },
		{ start: '2016-08-19', title: 'Statehood Day in Hawaii' },
		{ start: '2016-08-19', title: 'National Aviation Day' },
		{ start: '2016-08-21', title: 'Senior Citizens Day' },
		{ start: '2016-08-26', title: 'Women\'s Equality Day' },
		{ start: '2016-08-27', title: 'Lyndon Baines Johnson Day' },
		{ start: '2016-09-05', title: 'Labor Day' },
		{ start: '2016-09-09', title: 'California Admission Day' },
		{ start: '2016-09-10', title: 'Carl Garner Federal Lands Cleanup Day' },
		{ start: '2016-09-11', title: 'Patriot Day' },
		{ start: '2016-09-11', title: 'National Grandparents Day' },
		{ start: '2016-09-13', title: 'Eid al-Adha' },
		{ start: '2016-09-16', title: 'Constitution Day and Citizenship Day observed' },
		{ start: '2016-09-16', title: 'National POW/MIA Recognition Day' },
		{ start: '2016-09-17', title: 'Constitution Day and Citizenship Day' },
		{ start: '2016-09-18', title: 'Air Force Birthday' },
		{ start: '2016-09-22', title: 'September equinox' },
		{ start: '2016-09-22', title: 'Emancipation Day' },
		{ start: '2016-09-23', title: 'Native Americans\' Day' },
		{ start: '2016-09-25', title: 'Gold Star Mother\'s Day' },
		{ start: '2016-10-03', title: 'Rosh Hashana' },
		{ start: '2016-10-03', title: 'Muharram' },
		{ start: '2016-10-03', title: 'Child Health Day' },
		{ start: '2016-10-04', title: 'Feast of St Francis of Assisi' },
		{ start: '2016-10-09', title: 'Leif Erikson Day' },
		{ start: '2016-10-10', title: 'Columbus Day' },
		{ start: '2016-10-10', title: 'Columbus Day' },
		{ start: '2016-10-10', title: 'Native Americans\' Day' },
		{ start: '2016-10-10', title: 'Indigenous People\'s Day' },
		{ start: '2016-10-12', title: 'Yom Kippur' },
		{ start: '2016-10-13', title: 'U.S. Navy Birthday' },
		{ start: '2016-10-15', title: 'White Cane Safety Day' },
		{ start: '2016-10-17', title: 'First Day of Sukkot' },
		{ start: '2016-10-17', title: 'Boss\'s Day' },
		{ start: '2016-10-18', title: 'Alaska Day' },
		{ start: '2016-10-23', title: 'Last Day of Sukkot' },
		{ start: '2016-10-24', title: 'Shmini Atzeret' },
		{ start: '2016-10-25', title: 'Simchat Torah' },
		{ start: '2016-10-28', title: 'Nevada Day' },
		{ start: '2016-10-29', title: 'Diwali/Deepavali' },
		{ start: '2016-10-31', title: 'Halloween' },
		{ start: '2016-11-01', title: 'All Saints\' Day' },
		{ start: '2016-11-02', title: 'All Souls\' Day' },
		{ start: '2016-11-06', title: 'Daylight Saving Time ends' },
		{ start: '2016-11-08', title: 'Election Day' },
		{ start: '2016-11-08', title: 'Election Day' },
		{ start: '2016-11-10', title: 'Marine Corps Birthday' },
		{ start: '2016-11-10', title: 'Return Day Delaware' },
		{ start: '2016-11-11', title: 'Veterans Day' },
		{ start: '2016-11-24', title: 'Thanksgiving Day' },
		{ start: '2016-11-25', title: 'State Holiday' },
		{ start: '2016-11-25', title: 'Presidents\' Day' },
		{ start: '2016-11-25', title: 'Lincoln\'s Birthday/Lincoln\'s Day' },
		{ start: '2016-11-25', title: 'Black Friday' },
		{ start: '2016-11-25', title: 'American Indian Heritage Day' },
		{ start: '2016-11-27', title: 'First Sunday of Advent' },
		{ start: '2016-11-28', title: 'Cyber Monday' },
		{ start: '2016-12-06', title: 'St Nicholas\' Day' },
		{ start: '2016-12-07', title: 'Pearl Harbor Remembrance Day' },
		{ start: '2016-12-08', title: 'Feast of the Immaculate Conception' },
		{ start: '2016-12-12', title: 'The Prophet\'s Birthday' },
		{ start: '2016-12-12', title: 'Feast of Our Lady of Guadalupe' },
		{ start: '2016-12-13', title: 'U.S. National Guard Birthday' },
		{ start: '2016-12-17', title: 'Pan American Aviation Day' },
		{ start: '2016-12-17', title: 'Wright Brothers Day' },
		{ start: '2016-12-21', title: 'December Solstice' },
		{ start: '2016-12-23', title: 'Christmas Eve observed' },
		{ start: '2016-12-24', title: 'Christmas Eve' },
		{ start: '2016-12-24', title: 'Christmas Eve' },
		{ start: '2016-12-25', title: 'Chanukah/Hanukkah (first day)' },
		{ start: '2016-12-25', title: 'Christmas Day' },
		{ start: '2016-12-26', title: 'Kwanzaa (until Jan 1)' },
		{ start: '2016-12-26', title: 'Christmas Day observed' },
		{ start: '2016-12-26', title: 'Day After Christmas Day' },
		{ start: '2016-12-30', title: 'New Year\'s Eve observed' },
		{ start: '2016-12-31', title: 'New Year\'s Eve' }
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
    [ "E-cigarettes", "occasions" ],
    [ "Tobacco chew", "pinches"],
    [ "Cigars", "cigars" ],
    [ "Hookah", "hits" ],
    [ "Blunts", "blunts" ],
    [ "Smoked MJ", "grams" ],
    [ "Edible MJ", [ "mg THC", "occasions" ] ],
    [ "Fake MJ", "grams" ],
    [ "MJ concentrates", [ "grams", "occasions" ] ],
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
    "act_subst": encodeURIComponent(JSON.stringify(active_substances.toArray())),
    "task": "timeline-followback"
  };
  
  jQuery.get('../../code/php/session.php', data, function() {
    console.log('stored subject and session and act_subst: ' +  subject + ", " + session + ", " + encodeURIComponent(JSON.stringify(active_substances.toArray())));
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

var colors = [ "#C6CAED", "#ADA8BE", "#A28497", "#6F5E5C", "#4A5240" ];

jQuery(document).ready(function() {

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
    
  // add the session variables to the interface
  jQuery('#user_name').text("User: " + user_name);
  jQuery('#session-participant').val(subjid);
  jQuery('#session-name').val(session);

  storeSubjectAndName();

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
