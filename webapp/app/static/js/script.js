$("#dataform").submit(function(e) {
    e.preventDefault();
    alert("WER");

    console.log($("#dataform").serialize());
    //var formData = new FormData($("#dataform"));
    var fromData = false;
    //console.log(formData);
    $.ajax({
           type: "POST",
           url: "/processing",
           data: $("#dataform").serialize(),
           success: function(data)
           {
               alert(data);
           }
         });

    e.preventDefault();

});