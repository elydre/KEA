# add DEP/uf.kea

FUNC test_rec $i
	$i + 1 > print > test_rec
	END

0 >  test_rec
