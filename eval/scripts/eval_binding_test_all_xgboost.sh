echo "victor+cyrus+onno on ephraim"
python eval_binding.py --train_list=victor+cyrus+onno --test_list=ephraim xgboost

echo "victor+cyrus+onno on ephraim with synthetic"
python eval_binding.py --synthetic --train_list=victor+cyrus+onno --test_list=ephraim xgboost

echo "ephraim+victor+onno on cyrus"
python eval_binding.py --train_list=ephraim+victor+onno --test_list=cyrus xgboost
echo "ephraim+victor+onno on cyrus with synthetic"
python eval_binding.py --synthetic --train_list=ephraim+victor+onno --test_list=cyrus xgboost

echo "ephraim+cyrus+onno on victor"
python eval_binding.py --train_list=ephraim+cyrus+onno --test_list=victor xgboost
echo "ephraim+cyrus+onno on victor with synthetic"
python eval_binding.py --synthetic --train_list=ephraim+cyrus+onno --test_list=victor xgboost

echo "ephraim+cyrus+victor on onno"
python eval_binding.py --train_list=ephraim+cyrus+victor --test_list=onno xgboost
echo "ephraim+cyrus+victor on onno with synthetic"
python eval_binding.py --synthetic --train_list=ephraim+cyrus+victor --test_list=onno xgboost

