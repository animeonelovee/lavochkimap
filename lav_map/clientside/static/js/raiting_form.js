const rating = document.querySelector('form[name=rating-form]');

    rating.addEventListener("change", function(e){

        $.ajax({
            url: this.action,
            method: 'post',
	        dataType: 'html',
            data: $(this).serialize(),
            cache: false
        }).done(function (response) {
            $('#rating-form').html(response);
        });
        
    })