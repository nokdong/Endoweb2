/* EndoWeb main view Calendar */

(function endoCalendar() {

"use strict";
var yearNames = ["2016","2017","2018"];

var monthNames = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"];
var dayNames = ["일", "월", "화", "수", "목", "금", "토"];


/*
var monthNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct", "Nov", "Dec"];
var dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
*/
document.addEventListener("DOMContentLoaded", function(event){

    var theDate = new Date(); //renderCalendar 입장에서 전역변수로 선언되어 날짜가 변경되면 이 변수도 변경되어 rendarCalendar에 반영된다.

    /*  날짜 관련 여러가지(날짜, 요일, 달별 일수, 각 달의 첫날 요일을 알 수 있는 함수*/
    var DateObject = function DateObject(theDate){
        this.theDate = theDate.getDate(); //며칠인지 알수 있다.
        this.dayName = dayNames[theDate.getDay()]; //요일을 알 수 있다.
        this.theMonth = monthNames[theDate.getMonth()]; //월을 알 수 있다.
        this.theYear = theDate.getFullYear(); //년을 알 수 있다
        this.numDaysInMonth = new Date(theDate.getFullYear(), theDate.getMonth()+1, 0).getDate(); //그 달의 날짜수을 알 수있다.
        this.firstDayOfMonth = dayNames[new Date(theDate.getFullYear(), theDate.getMonth(), 1).getDay()]; //그 달의 1일의 요일을 알 수 있다
    };

    var currentDate = new DateObject(theDate); //첫 페이지 로딩 시 오늘 날짜를 입력한다.

    //달력을 렌더링한다. 년 or 달이 갱신 함수를 호출하고 이 함수를 리턴해서 달력을 다시 랜더링 한다
    function renderCalendar (targetElem){

        //타켓 요소에 div, class 를 쉽게 넣어주기 위한 함수
        function addElem(elementType, elemClass, appendTarget){
            appendTarget.innerHTML += "<" + elementType + " class =" + elemClass + "> </" + elementType + ">";
        };

        currentDate = new DateObject(theDate); // theDate 값이 변경됨에 따라 currentDate도 변경된다.

        var renderTarget = document.getElementById(targetElem); //달려 id를 획득한다.
        renderTarget.remove(); // 달력을 다시 랜더링 하기 전에 기존 달력을 제거한다.
        renderTarget = document.createElement('div'); // 같은 이름의 id로 달력 요소를 생성한다.
        renderTarget.id = targetElem;
        document.getElementsByTagName('body')[0].appendChild(renderTarget); // body 요소 밑에 달력을 추가한다.

        addElem("div", "month-view", renderTarget); // calendar 밑에 month-view를 만들었다. 추후 날짜별 요약창을 calenar 밑에 추가할 수 있다.
        var monthView = document.querySelector(".month-view");

        /* 년도를 선택할 수 있는 코드. 현재 년을 기본으로 설정한다. 년도가 바뀌면 yearChange를 호출한다.*/
        var yearMenu = document.createElement("select");
        yearMenu.id = "yearList";
        yearMenu.addEventListener("change", yearChange);

        for (var i=0; i<yearNames.length; i++){
            var year = document.createTextNode(yearNames[i]);
            var eachOption = document.createElement("option");
            if (yearNames[i] == currentDate.theYear) {
                eachOption.setAttribute("selected","selected");
            }
            eachOption.appendChild(year);
            yearMenu.appendChild(eachOption);
        };

        /* 월을 선택할 수 있는 코드. 현재 달을 기본으로 설정한다. 월이 바뀌면 monthChage 함수를 호출한다*/
        var monthMenu = document.createElement("select");
        monthMenu.id = "monthList";
        monthMenu.addEventListener("change", monthChange);

        for (i=0; i< monthNames.length; i++){
            var eachMonth = document.createTextNode(monthNames[i]);
            eachOption = document.createElement("option");
            if (monthNames[i] == currentDate.theMonth) {
                eachOption.setAttribute("selected","selected");
            }
            eachOption.appendChild(eachMonth);
            monthMenu.appendChild(eachOption);
        };

        var prevMonthSpan = document.createElement("SPAN");
        prevMonthSpan.addEventListener('click', function() {
            goToMonth(currentDate, false); // false면 이전달로 간다.
        });
        prevMonthSpan.classList.add('arrow', 'float-left','prev-arrow');
        prevMonthSpan.id = "prev-arrow";
        var backArrow = document.createTextNode("<");
        prevMonthSpan.appendChild(backArrow);

        var nextMonthSpan = document.createElement("SPAN");
        nextMonthSpan.addEventListener('click', function() {
            goToMonth(currentDate, true); //true면 다음달로 간다.
        });
        nextMonthSpan.classList.add('arrow','float-right','next-arrow');
        nextMonthSpan.id = "next-arrow";
        var nextArrow = document.createTextNode('>');
        nextMonthSpan.appendChild(nextArrow);

        // 달력의 head 부분 - 년, 달을 선택할 수 있는 부분 - 을 위한 코드
        var monthSpan = document.createElement("SPAN");
        monthSpan.className = "month-header";
        monthSpan.appendChild(prevMonthSpan);
        monthSpan.appendChild(yearMenu);
        var yearText = document.createTextNode("년 ");
        monthSpan.appendChild(yearText);
        monthSpan.appendChild(monthMenu);
        var monthText = document.createTextNode("월");
        monthSpan.appendChild(monthText);
        monthSpan.appendChild(nextMonthSpan)
        monthView.appendChild(monthSpan);

        //일 - 토 까지를 나열하는 영역
        for (i=0; i< dayNames.length; i++){
            var dayOfWeek = document.createElement('div');
            dayOfWeek.className = "day-of-week";
            var charOfDay = document.createTextNode(dayNames[i]);
            dayOfWeek.appendChild(charOfDay);
            monthView.appendChild(dayOfWeek);
        };

        // 1일부터 그달의 마지막 날까지 요일을 정렬한다.
        // 요일별로 시간을 time 요소 안에 넣어둔다. 나중에 이 부분을 이용해 데이타 베이스에서 정보를 추출한다.
        var calendarList = document.createElement("ul");
        for (i=0; i< currentDate.numDaysInMonth; i++){
            var calendarCell = document.createElement("li");
            var calCellTime = document.createElement("time");
            calendarList.appendChild(calendarCell);
            calendarCell.id='day_'+(i+1);
            var dayData = new Date(theDate.getFullYear(), theDate.getMonth(), (i+1));
            calCellTime.setAttribute('datetime', dayData);
            calCellTime.setAttribute('data-dayofweek', dayNames[dayData.getDay()]);

            calendarCell.className = "calendar-cell"; // 오늘 날짜에는 class 명을 today로 변경한다.
            if (i == currentDate.theDate -1){
                calendarCell.className="today";
            };
            var dayOfMonth = document.createTextNode(i+1);
            calCellTime.appendChild(dayOfMonth);
            calendarCell.appendChild(calCellTime);
            monthView.appendChild(calendarList);
        };

        // 각 달의 첫번째 날짜를 달력에서 알맞게 배치한다.
        var dayOne = document.getElementById('day_1');
        if (currentDate.firstDayOfMonth == "월"){
            dayOne.style.marginLeft = "49px";
        } else if (currentDate.firstDayOfMonth == "화"){
            dayOne.style.marginLeft = "98px";
        } else if (currentDate.firstDayOfMonth == "수"){
            dayOne.style.marginLeft = "147px";
        } else if (currentDate.firstDayOfMonth == "목") {
            dayOne.style.marginLeft = "196px";
        } else if (currentDate.firstDayOfMonth == "금") {
            dayOne.style.marginLeft = "245px";
        } else if (currentDate.firstDayOfMonth == "토") {
            dayOne.style.marginLeft = "304px";
        };


    } // renderCalendar function ends

    renderCalendar("calendar");

    function yearChange() {
        var year = document.getElementById("yearList");
        theDate = new Date(Number(year.options[year.selectedIndex].text), theDate.getMonth(), 1);
        return renderCalendar("calendar");
    };

    function monthChange(){
        var month = document.getElementById("monthList");
        theDate = new Date(theDate.getFullYear(),  month.selectedIndex, 1);
        return renderCalendar("calendar");
    };

    function goToMonth(currentDate, direction) {
        if (direction==false) {
            theDate = new Date(theDate.getFullYear(), theDate.getMonth()-1,1);
        } else {
            theDate = new Date(theDate.getFullYear(), theDate.getMonth()+1, 1)
        }
        return renderCalendar("calendar");
    };


    }); // DOMContentLoaded event listener ends

})(); //iife ends