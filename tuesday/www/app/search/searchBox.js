app.controller("SearchController",
function ($rootScope, $scope, $location) {
    $scope.currentPath = '/';
    $scope.hide = false;
    $scope.disabled = true;
    $scope.searchTypes = {
        'token': 'Token',
        'lemma': 'Lemma',
        'stem': 'Stem',
    };

    $scope.reset = function () {
        nodes = $location.path().split('/');

        if (nodes.length > 2 && nodes[1] === 'rank') {
            $scope.searchText = nodes[2];

            query = $location.search();
            field = query['field'];
            if (field != undefined)
                $scope.field = field;
            else
                $scope.field = 'token';
        }
        else {
            $scope.field = 'token';
            $scope.searchText = null;
        }

        $scope.searchPlaceholder = "search for...";
        $scope.switchSearchType($scope.field);
    };

    $scope.switchSearchType = function (field) {
        $scope.field = field;
        $scope.goTitle = $scope.searchTypes[field];
        $scope.dropDownOpen = false;
    };

    $scope.search = function () {
        var query = $location.search();

        params = {}
        if ($scope.field != 'token') {
            params.field = $scope.field;
        }
        if ('limit' in query && query.limit != 10)
            params.limit = query.limit;
        if ('corpus' in query && query.corpus != '')
            params.corpus = query.corpus;

        var url = "/rank/" + $scope.searchText;
        var query = $.param(params);
        if (query !== '') {
            url = url + '?' + query;
        }

        $scope.reset();
        $location.hash(null);
        $location.url(url);
    };

    $scope.onNewLocation = function (newValue, oldValue) {
        $scope.currentPath = newValue;
        if ($scope.hideOnHome || null)
            $scope.hide = ($scope.currentPath == '/')
        $scope.reset();
    };

    /************************************************************************************************
     * Initialize
     */
    $scope.$watch('searchText', function (term) {
        $scope.disabled = $scope.searchText == null || $scope.searchText.length == 0;
    });

    $scope.reset();
});

app.directive('searchBox', function ($location) {
    var config = {
        restrict: 'EA',
        scope: {
            hideOnHome: '='
        },
        templateUrl: 'app/search/searchTemplate.html',
        controller: 'SearchController',
        link: function (scope, element, attrs) {
            scope.$watch(function () {
                return $location.$$path;
            }, scope.onNewLocation);
        }
    }

    return config;
});