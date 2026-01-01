document.addEventListener('activityCheckboxChanged', function (e) {
  const { type, checked } = e.detail;
  //console.log('checkbox changed:', type, checked);
  if (window._activityCheckboxNotify) window._activityCheckboxNotify(type, checked);

    //grab the current state of all checkboxes
    const state = {};
    document.querySelectorAll('input[type=checkbox][id^="toggle-"]').forEach(cb => {
        const actType = cb.id.replace('toggle-', '');
        state[actType] = cb.checked;
    });
    console.log('Current checkbox state:', state);

    //
    

});