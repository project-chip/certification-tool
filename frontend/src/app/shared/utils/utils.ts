export function getTimeStamp() {
  const dateTime = new Date();
  const title = dateTime.getFullYear() + '_' + (dateTime.getMonth() + 1).toString().padStart(2, '0') + '_' +
    dateTime.getDate().toString().padStart(2, '0') + '_' + dateTime.getHours().toString().padStart(2, '0') + '_'
    + dateTime.getMinutes().toString().padStart(2, '0') + '_' + dateTime.getSeconds().toString().padStart(2, '0');
  return title;
}

export function addThemeSwitchClass(value: any) {
  document.getElementsByTagName('body')[0].className = '';
  document.getElementsByTagName('body')[0].classList.add(value.code);
}
