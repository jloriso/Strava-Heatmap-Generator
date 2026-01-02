document.addEventListener('activityCheckboxChanged', function (e) {
  const { type, checked } = e.detail;
  //console.log('checkbox changed:', type, checked);
  if (window._activityCheckboxNotify) window._activityCheckboxNotify(type, checked);

    //grab the current state of all checkboxes
    const state = {};
    document.querySelectorAll('input[type=checkbox][id^="toggle-"]').forEach(cb => {
        const actType = cb.id.replace('toggle-', '');
        state[actType] = cb.checked;
        if(state[actType] == false) 
        {
            //if unchecked, remove all activities of this type from the map
            console.log('Removing activities of type:', actType);

        }
        else{
            //if checked, add all activities of this type to the map
            console.log('Adding activities of type:', actType);
        }
    });
});

function initAllActivityCheckboxes() {
  document.querySelectorAll('input[type=checkbox][id^="toggle-"]').forEach(cb => {
    const type = cb.id.replace('toggle-', '');
    if (!cb.checked) {
      cb.checked = true;
      document.dispatchEvent(
        new CustomEvent('activityCheckboxChanged', { detail: { type, checked: true } })
      );
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllActivityCheckboxes);
} else {
  initAllActivityCheckboxes();
}