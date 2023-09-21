import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'highlightSearch'
})
export class HighlightSearchPipe implements PipeTransform {

  transform(value: any, args: any): any {
    if (!args[0]) {
      return value;
    }

    const regex = new RegExp(args[0], 'gi');
    const match = value.match(regex);

    if (!match) {
      return value;
    }

    const activeClass = args[1] ? ' active_log' : '';

    return value.replace(regex, function (matchKey: any) {
      return '<span class="highlight_log_search' + activeClass + '">' + matchKey + '</span>';
    });
  }

}
