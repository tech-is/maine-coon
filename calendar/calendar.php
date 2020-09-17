<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="calendar.css">
    <title>Calendar</title>
</head>
<body>
    <?php 
    date_default_timezone_set('Asia/Tokyo');
    // 年設定
    $Y=date('Y');
    // 月設定
    $m=date('m');
    // 日付設定
    $d=date('d');
    // 曜日の設定->0~6
    $weeks=array('日','月','火','水','木','金','土');
    // submitされるたびに、$Yと$mを更新
    if(isset($_POST['Y'])){
        $Y=$_POST['Y'];
    }
    if(isset($_POST['m'])){
        $m=$_POST['m'];
    }
    if(isset($_POST['change'])){
        if($_POST['change']=='<'){
            if($m==1){
                $Y--;
                $m=12;
            }else{
                $m--;
            }
        }else{
            if($m==12){
                $Y++;
                $m=1;
            }else{
                $m++;
            }
        }
        // $_POST['change']の削除
        unset($_POST['change']);
    }
    // 1日目の曜日取得
    $week1=date('w',strtotime($Y.$m.'01'));
    // 月末日取得
    $t=date('t',strtotime($Y.$m.'01'));
    // 最終日の曜日取得,曜日は0~6であらわされる。
    $week2=date('w',strtotime($Y.$m.$t));
    
    $calendar=[];
    // $jは横の列,$iが一週間ごと
    $j=0; 
 
    // 1日までの空欄を作成
    for($i=0;$i<$week1;$i++){
        $calendar[$j][]='';
    }

    // 1日から月曜日までのループ
    for($i=1;$i<=$t;$i++){
        if(isset($calendar[$j]) && count($calendar[$j])==7){
            $j++;
        }
        $calendar[$j][]=$i++;
    }

    // 月末の空欄作成
    for($i=count($calendar[$j]);$i<7;$i++){
        $calendar[$j][]='';
    }
   
    ?>
    <table class="calendar">
        <caption colspan="7">
        <!-- ボタン押した変化をどうする -->
            <form action="" method="POST">
                <input type="hidden" name="m" value="<?=$m?>">
                <input type="hidden" name="Y" value="<?=$Y?>">
                <input type="submit" name="change" value="<">
            <?php echo $Y.'年'.$m.'月'?>
                <input type="submit" name="change" value=">">
            </form>
        </caption>
        <thred>
            <tr>
                <!-- 曜日を決める -->
                <?php foreach($weeks as $week):?>
                <td><?php echo $week?></td>
                <?php endforeach?>
            </tr>
        </thred>
        <tbody>
        <!-- $calendarの中身をforeachで表す。($calendar[$j]) -->
        <?php foreach($calendar as $tr):?>
            <tr>
            <!-- $trの中身をforeachで表す。 ($calendar[$j][$i])-->
                <?php foreach($tr as $td):?>
                <td>
                <?php echo $td;?>
                </td>
                <?php endforeach?>
            </tr>
            <?php endforeach?>
        </tbody>
    </table>
</body>
</html>