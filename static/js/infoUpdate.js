$(document).ready(function() {
        $(document).on('change', '#id_Dx', autoInputFollowup);
        $(document).on('click','#button', followupDateCal);
        $('#id_date, #id_birth').datepicker({
            dayNamesMin: [ "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat" ],
            monthNamesShort: ['1','2','3','4','5','6','7','8','9','10','11','12'],
            dateFormat:'yy-mm-dd',
            changeMonth:true,
            changeYear: true,
            yearRange:"1910:2018",
        });
        $("#id_type, #id_procedure").css({
            "list-style-type": "none",
            "display": "inline-block",
            "text-align":"left",
            "padding":"0px"
            });

        function followupDateCal() {
            var examDate = document.getElementById("id_date").value;
            var arr = examDate.split('-');
            var currentDate = new Date(arr[0], arr[1]-1, arr[2]);
            var followupPeriod = document.getElementById("id_followup_period").value;
            var followupDate = new Date(currentDate.setMonth(currentDate.getMonth()+Number(followupPeriod)));
            var year = followupDate.getFullYear();
            var month = followupDate.getMonth()+1;
            var date = followupDate.getDate();
            finalDate = year + '-' + month + '-' + date;
            $('#hidden').val(finalDate);
        }

        function autoInputFollowup() {
            var twoFour = "csg atrophic gastritis erythematous gastritis colon polyp colon polyps";
            var twelve = "erosive gastritis erosive gastritis r/o erosive gastritis erosion  gastric polyps  gastric polyp";
            var two = "gastric ulcer";
            var sixty = "nl w.n.l";
            var Dx = document.getElementById("id_Dx").value;
            Dx = Dx.toLowerCase();
            if (two.includes(Dx)) {
                document.getElementById("id_followup_period").value = 2;
            } else if (twelve.includes(Dx)) {
                document.getElementById("id_followup_period").value = 12;
            } else if (twoFour.includes(Dx)) {
                document.getElementById("id_followup_period").value = 24;
            } else if (sixty.includes(Dx)) {
                document.getElementById("id_followup_period").value = 60;
            };
        };
        var btn = document.getElementById("button");
        btn.onclick = function () {
            var childWindow = window.parent;
            var parentWindow = childWindow.opener;
            var examDate = document.getElementById("id_date").value;
            parentWindow.reload(examDate);
        };
})