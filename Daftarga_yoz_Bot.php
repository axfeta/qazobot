<?php
ob_start();
error_reporting(0);
define("API_KEY",'token');
$admin = "1655818396"; //97-qatordai admin idni tahrirlang
$botname = bot('getme',['bot'])->result->username;
function bot($method,$datas=[]){
$url = "https://api.telegram.org/bot".API_KEY."/$method";
$ch = curl_init();
curl_setopt($ch,CURLOPT_URL,$url);
curl_setopt($ch,CURLOPT_RETURNTRANSFER,true);
curl_setopt($ch,CURLOPT_POSTFIELDS,$datas); 
$res = curl_exec($ch);
if(curl_error($ch)){
var_dump(curl_error($ch));
}else{
return json_decode($res);
}
}
$update = json_decode(file_get_contents('php://input'));
$message = $update->message;
$mid = $message->message_id;
$data = $update->callback_query->data;
$type = $message->chat->type;
$text = $message->text;
$cid = $message->chat->id;
$uid= $message->from->id;
$message = $update->message;
$cid = $message->chat->id;
$cidtyp = $message->chat->type;
$miid = $message->message_id;
$name = $message->chat->first_name;
$user1 = $message->from->username;
$tx = $message->text;
$sana = date('H:i:s', strtotime('2 huor'));
$soat = date('d-m-Y',strtotime('2 huor'));
 
$type = $message->chat->type;
$Name = $message->chat->first_name;
$user = $message->from->username;
$guruhlar = file_get_contents("Stat/guruh.dat");
$kanallar = file_get_contents("Stat/kanal.dat");
$step = file_get_contents("Bot/$cid.step");
$step2 = file_get_contents("Bot/2.step");
$step4 = file_get_contents("Bot/4.step");
$step3 = file_get_contents("Bot/3.step");
$step1 = file_get_contents("Bot/$chat_id2.step");
if ($text == "/start") {
    $image_url = 'https://viscovbt.alwaysdata.net/ms/ms.jpeg';
    bot('sendPhoto', [
        'chat_id' => $cid,
        'photo' => $image_url,
        'caption' => "<b>👋 Assalomu Alaykum
✍️ Menga xohlagan matnni yozib yuboring, men uni siz uchun daftarga yozib rasmini tashayman.</b>",
        'parse_mode' => "html",
        'reply_markup' => json_encode([
            'inline_keyboard' => [
                [
                    ['text' => '🛍️ Botga buyurtma berish', 'url' => 'https://t.me/OrtiqovIxtiyorBot'],
                ],
            ],
        ]),
    ]);
}




if($text != '/start' and $text!='/panel' and $text!='📊Statistika' and $text!='👤Foydalanuvchilarga xabarlar yuborish'){
bot('deletemessage',[
'chat_id'=>$cid,
'message_id'=>$mid +1,
]);
   bot('sendphoto',[
   'chat_id'=>$cid,
   'photo'=>"https://apis.xditya.me/write?text=$text",
   'caption'=>"$text\n\n@$botname",
   'parse_mode'=>"html",
]);
}
$panel = json_encode([
'resize_keyboard'=>true,
'keyboard'=>[
[['text'=>"📊Statistika"],['text'=>"👤Pochta bo'limi"]],
[['text'=>"/start"]], 
]
]);

if($text=="/panel" and $cid==$admin){
	bot('SendMessage',[
	'chat_id'=>$cid,
	'reply_to_message_id'=>$mid,
	'parse_mode'=>'markdown',
	'text'=>"👨‍💻 Admin paneliga xush kelibsiz!",
	'reply_markup'=>$panel,
	]);
	}

$soat = date('H:i:s', strtotime('2 hour'));
$date = date('d-M-Y', strtotime('2 hour'));
$admin = "1655818396";
$type = $message->chat->type;
if($type =="private"){
$baza = file_get_contents("mrax.txt");
    if(mb_stripos($baza, $cid) !== false){
}else{
file_put_contents("mrax.txt", "$baza\n$cid");
}    
}

if($text == "📊Statistika" and $cid==$admin){
	$stat = file_get_contents("mrax.txt");
	$count = substr_count($stat,"\n");
	bot('sendmessage',[
	  'chat_id'=>$cid, 
	'text'=>"📊Bot statistikasi\n\n👤Botdagi odamlar soni: $count\n\n⏰vaqt: $soat\n📆Sana: $date", 
]);
} 

/*$guruh = file_get_contents("mrax.txt");*/

$kanal = file_get_contents("kanal.db");
$mrax = file_get_contents("mrax.db");
$xabar = file_get_contents("xabarlar.txt");
if($type=="private"){
if(strpos($mrax,"$cid") !==false){
}else{
file_put_contents("mrax.db","$mrax\n$cid");
}
} 
$reply = $message->reply_to_message->text;
$rpl = json_encode([
            'resize_keyboard'=>false,
            'force_reply'=>true,
            'selective'=>true
        ]);
        $repl = json_encode([
        'resize_keyboard'=>false,
        'selective'=>true,
        ]);
if($text=="👤Pochta bo'limi" and $cid==$admin){
  bot('sendmessage',[
    'chat_id'=>$cid,
    'text'=>"👤Foydalanuvchilarga yubormoqchi bo'lgan xabar matnini kiriting! Bekor qilish uchun /cancel ni bosing",
    'parse_mode'=>"html",
]);
    file_put_contents("xabarlar.txt","user");
}
if($xabar=="user" and $cid==$admin){
if($text=="/cancel"){
  file_put_contents("xabarlar.txt","");
}else{
  $lich = file_get_contents("mrax.db");
  $mrax = explode("\n",$lich);
  foreach($mrax as $lichkalar){
  $okuser=bot("sendmessage",[
    'chat_id'=>$lichkalar,
    'text'=>$text,
    'parse_mode'=>'markdown'
]);
}
if($okuser){
  bot("sendmessage",[
    'chat_id'=>$cid,
    'text'=>"✅Barcha foydalanuvchilarga yuborildi!",
    'parse_mode'=>'html',
]);
  file_put_contents("xabarlar.txt","");
}
}
}
if($text=="/cancel" and $cid==$admin){
bot('sendmessage',[
'chat_id'=>$cid,
'text'=>"*Xabar bekor qilindi✅*",
'parse_mode'=>'markdown',
'reply_markup'=>$panel,
]);
}