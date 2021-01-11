/* globals Chart:false, feather:false */

(function () {
  'use strict'

  feather.replace()

  // Graphs
  var ctx = document.getElementById('myChart')

  // eslint-disable-next-line no-unused-vars
  var myChart = new Chart(ctx, {
    type: 'bar',//'line'
    data: {
      labels: [
        'Sunday',
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday'
      ],
      datasets: [{
        data: [
          15339,
          21345,
          18483,
          24003,
          23489,
          24092,
          12034
        ],
        lineTension: 0,
        backgroundColor: 'blue',//'transparent',
        borderColor: '#007bff',
        borderWidth: 4,
        pointBackgroundColor: '#007bff'
      }]
    },
    options: {
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: false
          }
        }]
      },
      legend: {
        display: false
      }
    }
  })
})()

function sp_del(id_) {
  let url_ = "/ajax-sp-del";
  ajax_data(id_, url_)
}

function sp_add() {
  let sp = input.value;
  let url_ = "/ajax-sp-add";
  if (sp.trim() != '')
    ajax_data(sp, url_);
}

let input = document.getElementById('input_phrase');

input.addEventListener("keyup", function (event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    document.getElementById("add-sp").click();
    this.value = '';
  }
});

function set_table(data) {
  let html_data = '';
  for (r of data) {
    html_data += '\
    <tr>\
      <td scope="row">\
      <a href="/ads/' + r.id + '">' + r.phrase + '</a>\
      </td>\
      <td>' + r.total_ads + '</td>\
      <td>' + r.total_ads_closed + '</td>\
      <td>\
        <a class="link" onclick="sp_del(' + r.id + '); return true;">del' + r.id + '</a>\
      </td>\
    </tr>'
  }
  document.getElementById('main-tbody').innerHTML = html_data;
}

function ajax_data(param, url_) {
  let data = new Object();
  let res = '';
  data.param = param;
  $.ajax({
    type: "POST",
    url: url_,
    data: data,
  }).done(function (response) {
    set_table(response);
  }).fail(function () {
    console.log('ajax error(((');
  });

  return res
}