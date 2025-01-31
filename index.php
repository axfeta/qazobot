<?php
$apiUrl = 'https://my.ucell.uz/Account/Login';

$data = array(
    'phone_number' => 'nomeriz',  ///nomeriz yozasiz + qoʻymasdan
    'password' => 'parol',  ///ucell uzdan kirilgandagi parol 
    'ot_password' => '935333', /// raqamingizni bosh 6 ta raqami 93 kod bo'lsa undan keyingi 4 ta raqam 
    'pin' => '',  /// pin kod bosa qoʻyiladi
    'login_type' => '3',    ///teginmang      
    'return_url' => '/'       ///teginmang        
);

$ch = curl_init($apiUrl);

curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data)); 
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
    'Content-Length: ' . strlen(http_build_query($data))
));

$response = curl_exec($ch);

if(curl_errno($ch)) {
    echo 'Error:' . curl_error($ch);
} else {
    echo 'Response:' . $response;
}

curl_close($ch);
?>